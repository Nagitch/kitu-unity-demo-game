#!/usr/bin/env python3
"""Generate and check the human-readable Arena v1 message contract.

Install tools/requirements-contracts.txt for checks. Rendering uses only stdlib.
Schemas validate message shape; gameplay timing and admission remain covered by
Rust behavior tests. No remote schema retrieval is permitted.
"""
import argparse
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/contracts/arena-v1'
DOC = ROOT / 'docs/specs/arena-events.md'
BEGIN = '<!-- BEGIN GENERATED ARENA CONTRACT -->'
END = '<!-- END GENERATED ARENA CONTRACT -->'


def decode(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def load(path):
    return decode(path.read_text())


def contract(base=BASE):
    catalog = load(base / 'catalog.json')
    schema = load(base / catalog['schema'])
    entries = catalog['messages']
    addresses = [entry['address'] for entry in entries]
    if len(addresses) != len(set(addresses)):
        raise ValueError('Duplicate catalog address')
    if catalog['contractVersion'] != 1:
        raise ValueError('Unsupported contract version')
    for entry in entries:
        if 'payload' in entry and (entry['payload'] not in schema['$defs'] or
                                  entry['arguments'] != [{'name': 'payload', 'type': 'str'}]):
            raise ValueError(f'Invalid JSON payload binding: {entry["address"]}')
    def refs(value):
        if isinstance(value, dict):
            if '$ref' in value:
                reference = value['$ref']
                if not reference.startswith('#/$defs/') or reference[8:] not in schema['$defs']:
                    raise ValueError(f'Only resolved local schema references are allowed: {reference}')
            for child in value.values():
                refs(child)
        elif isinstance(value, list):
            for child in value:
                refs(child)
    refs(schema)
    return entries, schema


def anchor(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def describe(schema):
    if '$ref' in schema:
        name = schema['$ref'].split('/')[-1]
        return f'[{name}](#type-{anchor(name)})'
    if 'const' in schema:
        return '`' + json.dumps(schema['const']) + '`'
    if 'enum' in schema:
        return ', '.join('`' + json.dumps(v) + '`' for v in schema['enum'])
    if 'anyOf' in schema:
        return ' or '.join(describe(v) for v in schema['anyOf'])
    kind = schema.get('type', 'value')
    scalars = {
        ('integer', -(2**31), 2**31 - 1): 'i32',
        ('integer', -(2**63), 2**63 - 1): 'i64',
        ('integer', 0, 2**32 - 1): 'u32',
        ('integer', 0, 2**64 - 1): 'u64',
        ('number', -3.4028234663852886e38, 3.4028234663852886e38): 'finite f32',
    }
    scalar = scalars.get((kind, schema.get('minimum'), schema.get('maximum')))
    if scalar:
        return '`' + scalar + '`'
    if kind == 'array':
        result = 'array of ' + describe(schema['items'])
        if schema.get('minItems') == schema.get('maxItems') and 'minItems' in schema:
            result += f' (exactly {schema["minItems"]})'
        elif 'maxItems' in schema:
            result += f' (at most {schema["maxItems"]})'
        return result
    if kind == 'object' and isinstance(schema.get('additionalProperties'), dict):
        return 'map from string to ' + describe(schema['additionalProperties'])
    result = '`' + kind + '`'
    if 'minimum' in schema or 'maximum' in schema:
        result += f' ({schema.get("minimum", "−∞")}…{schema.get("maximum", "+∞")})'
    if 'pattern' in schema:
        result += f'; pattern `{schema["pattern"]}`'
    return result


def fields(schema):
    lines = ['| Field | Type / range | Required | Meaning |', '| --- | --- | --- | --- |']
    for key, value in schema['properties'].items():
        lines.append(f'| `{key}` | {cell(describe(value))} | {"yes" if key in schema.get("required", []) else "no"} | {cell(value.get("description", "—"))} |')
    return '\n'.join(lines)


def render(base=BASE):
    entries, schema = contract(base)
    raw_notes = (base / 'semantics.md').read_text()
    sections = re.split(r'^## (/[^\n]+)\n', raw_notes, flags=re.M)
    if len(sections[1::2]) != len(set(sections[1::2])):
        raise ValueError('Duplicate semantics section')
    notes = dict(zip(sections[1::2], sections[2::2]))
    if set(notes) != {e['address'] for e in entries}:
        raise ValueError('Semantics sections must cover the catalog exactly')
    examples = load(base / 'examples/messages.json')
    lines = [BEGIN, '', f'This reference covers **{len(entries)} OSC addresses**. Tables and examples are generated; behavioral notes are authored in [semantics.md](../contracts/arena-v1/semantics.md).', '']
    for category in dict.fromkeys(e['category'] for e in entries):
        lines += ['## ' + category, '', '| Address | Meaning |', '| --- | --- |']
        for entry in entries:
            if entry['category'] == category:
                a = entry['address']
                lines.append(f'| [`{a}`](#{anchor(a)}) | {entry["summary"]} |')
        lines.append('')
    lines += ['## Message details', '']
    for entry in entries:
        address = entry['address']
        lines += [f'<a id="{anchor(address)}"></a>', '', f'### `{address}`', '', entry['summary'] + '.', '', notes[address].strip(), '',
                  f'Implementation: [{entry["source"]}](../../{entry["source"]}).', '',
                  '| Argument index | Name | OSC tag | Meaning |', '| --- | --- | --- | --- |']
        for index, arg in enumerate(entry['arguments']):
            description = arg.get('description', 'JSON document matching the payload definition below.')
            lines.append(f'| {index} | `{arg["name"]}` | `{arg["type"]}` | {description} |')
        if not entry['arguments']:
            lines.append('| — | — | — | No arguments; an empty args array is required. |')
        lines.append('')
        if 'payload' in entry:
            name = entry['payload']
            payload = schema['$defs'][name]
            lines += [f'Payload: [{name}](#type-{anchor(name)}).', '']
            for variant in payload.get('oneOf', [payload]):
                if 'title' in variant:
                    lines += ['**' + variant['title'] + '**', '']
                lines += [fields(variant), '']
        relevant = [(i, x) for i, x in enumerate(examples) if x['message']['address'] == address]
        lines += ['Examples: ' + ', '.join(f'[{x["name"]}](../contracts/arena-v1/examples/messages.json)' for _, x in relevant) + '.', '']
        if relevant:
            example = relevant[0][1]['message']
            value = decode(example['args'][0]['value']) if 'payload' in entry else example
            encoded = json.dumps(value, indent=2, ensure_ascii=False)
            if len(encoded) < 1600:
                if 'payload' in entry:
                    lines += ['Decoded JSON payload example (inside OSC `args[0].value`):', '']
                lines += ['```json', encoded, '```', '']
            elif 'payload' in entry:
                lines += ['The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.', '']
    lines += ['## Payload and shared type reference', '', 'All object fields are required unless explicitly marked optional. Objects reject unregistered fields in the producer contract. Every nested type is linked below.', '']
    for name, definition in schema['$defs'].items():
        lines += [f'<a id="type-{anchor(name)}"></a>', '', '### ' + name, '']
        for variant in definition.get('oneOf', [definition]):
            if 'title' in variant:
                lines += ['**' + variant['title'] + '**', '']
            if 'properties' in variant:
                lines += [fields(variant), '']
            else:
                lines += [describe(variant), '']
    return '\n'.join(lines + [END])


def document(write=False, base=BASE, path=DOC):
    text = path.read_text()
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError('Reference must have exactly one generated region')
    start, stop = text.index(BEGIN), text.index(END) + len(END)
    expected = text[:start] + render(base) + text[stop:]
    if write:
        path.write_text(expected)
    elif expected != text:
        raise ValueError('Event reference is stale; run python3 tools/arena_contracts.py generate')


class Validator:
    def __init__(self, base=BASE):
        from jsonschema import Draft202012Validator
        self.entries, schema = contract(base)
        Draft202012Validator.check_schema(schema)
        self.by_address = {e['address']: e for e in self.entries}
        self.schema = schema
        self.factory = Draft202012Validator
        self.validators = {name: Draft202012Validator(dict(schema, **{'$ref': '#/$defs/' + name}))
                           for name in schema['$defs']}
        self.coverage = set()
        self.variants = set()
        self.count = 0

    def message(self, message, *, nested=False):
        if set(message) != {'address', 'args'} or not isinstance(message['args'], list):
            raise ValueError('Expected exact typed OSC message keys address and args')
        address = message['address']
        if address not in self.by_address:
            raise ValueError('Unregistered Arena address: ' + address)
        entry = self.by_address[address]
        if nested != (entry['category'] == 'TSQ1 clip messages'):
            raise ValueError('Cue assignments must be nested in TSQ1, not top-level output')
        args = message['args']
        if len(args) != len(entry['arguments']):
            raise ValueError('Wrong OSC argument count: ' + address)
        for value, spec in zip(args, entry['arguments']):
            self.validators['WireArg'].validate(value)
            if value['type'] != spec['type']:
                raise ValueError('Wrong OSC argument tag: ' + address)
            if value['type'] == 'float' and not math.isfinite(value['value']):
                raise ValueError('Nonfinite OSC float: ' + address)
            for key, test in [('minimum', lambda a,b:a >= b), ('maximum', lambda a,b:a <= b)]:
                if key in spec and not test(value['value'], spec[key]):
                    raise ValueError('OSC argument out of range: ' + address)
        if 'payload' in entry:
            payload = decode(args[0]['value'])
            self.validators[entry['payload']].validate(payload)
            for index, variant in enumerate(self.schema['$defs'][entry['payload']].get('oneOf', [])):
                candidate = dict(variant, **{'$defs': self.schema['$defs']})
                if self.factory(candidate).is_valid(payload):
                    self.variants.add((address, index))
            if address == '/ui/arena/timeline/event' and payload['kind'] == 'event':
                for child in payload['bundle']['messages']:
                    expected = '/render/arena/cue/' + ('boss' if payload['clipId'] == 'boss-telegraph' else 'floor')
                    if child['address'] != expected:
                        raise ValueError('Timeline clip contains the wrong cue address')
                    self.message(child, nested=True)
        self.coverage.add(address)
        self.count += 1

    def complete(self):
        missing = set(self.by_address) - self.coverage
        variants = {(e['address'], i) for e in self.entries if 'payload' in e
                    for i, _ in enumerate(self.schema['$defs'][e['payload']].get('oneOf', []))}
        if missing or variants - self.variants:
            raise ValueError(f'Missing address/variant coverage: {sorted(missing)}, {sorted(variants-self.variants)}')


def source_coverage(entries):
    # A guard against new literal routes in the Arena implementation. Behavioral
    # and runtime checks are still required; this is not a Rust parser.
    paths = [ROOT / 'app/src/arena.rs', *sorted((ROOT / 'app/src/arena').rglob('*.rs'))]
    found = set()
    for path in paths:
        if path.name == 'tests.rs':
            continue
        found.update(re.findall(r'"(/(?:input|game|render|ui)/arena/[^"\s]+)"', path.read_text()))
    expected = {e['address'] for e in entries}
    if found != expected:
        raise ValueError(f'Catalog/source address drift: undocumented={sorted(found-expected)}, missing={sorted(expected-found)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['generate', 'check'])
    parser.add_argument('--trace', type=Path, help='Validate every typed message in a Rust-produced NDJSON trace')
    args = parser.parse_args()
    try:
        document(write=args.action == 'generate')
        if args.action == 'check':
            validator = Validator()
            source_coverage(validator.entries)
            names = set()
            for example in load(BASE / 'examples/messages.json'):
                if example['name'] in names:
                    raise ValueError('Duplicate example name')
                names.add(example['name'])
                validator.message(example['message'], nested=example.get('context') == 'clip')
            validator.complete()
            print(f'Contract and generated reference: {len(validator.entries)} addresses, {len(names)} examples passed')
            if args.trace:
                runtime = Validator()
                with args.trace.open() as stream:
                    for line_no, line in enumerate(stream, 1):
                        try:
                            runtime.message(decode(line))
                        except Exception as error:
                            raise ValueError(f'{args.trace}:{line_no}: {error}') from error
                runtime.complete()
                print(f'Runtime trace: {runtime.count} messages, all addresses and payload variants passed')
    except (ValueError, OSError, ImportError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
