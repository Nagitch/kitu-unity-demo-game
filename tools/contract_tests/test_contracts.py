"""Negative regressions for the spec/implementation contract boundary."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import arena_contracts as contracts
from jsonschema import ValidationError


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = contracts.Validator()
        self.examples = contracts.load(contracts.BASE / 'examples/messages.json')

    def message(self, address):
        return copy.deepcopy(next(e['message'] for e in self.examples
                                  if e['message']['address'] == address))

    def rejects(self, message, **kwargs):
        with self.assertRaises((ValueError, ValidationError)):
            self.validator.message(message, **kwargs)

    def change_payload(self, message, mutate):
        value = json.loads(message['args'][0]['value'])
        mutate(value)
        message['args'][0]['value'] = json.dumps(value)
        return message

    def test_unknown_address_and_extra_osc_argument_fail(self):
        self.rejects({'address': '/game/arena/new-unregistered', 'args': []})
        self.rejects({'address': '/input/arena/start', 'args': [{'type': 'bool', 'value': True}]})

    def test_exact_tag_and_integer_range_are_checked(self):
        frame = self.message('/input/arena/frame')
        frame['args'][0] = {'type': 'int', 'value': 0}
        self.rejects(frame)
        use = self.message('/input/arena/use')
        use['args'][0]['value'] = 2**31
        self.rejects(use)
        use['args'][0]['value'] = True
        self.rejects(use)

    def test_missing_field_unknown_field_and_nested_casing_fail(self):
        self.rejects(self.change_payload(self.message('/game/arena/damage'), lambda p:p.pop('health')))
        self.rejects(self.change_payload(self.message('/game/arena/damage'), lambda p:p.update(unregistered=True)))
        def rename(p):
            p['enemies'] = [{'id': 1}]
        self.rejects(self.change_payload(self.message('/ui/arena/state'), rename))

    def test_variant_specific_fields_cannot_be_interchanged(self):
        attack = copy.deepcopy(next(e['message'] for e in self.examples
                                   if e['name'] == 'game-arena-attack-player-weapon'))
        self.rejects(self.change_payload(attack, lambda p:p.update(kind='grenade')))

    def test_duplicate_keys_and_nonfinite_numbers_fail(self):
        command = self.message('/ui/arena/command')
        command['args'][0]['value'] = '{"accepted": true, "accepted": false}'
        self.rejects(command)
        frame = self.message('/input/arena/frame')
        frame['args'][0]['value'] = float('nan')
        self.rejects(frame)

    def test_clip_arguments_context_and_range_fail(self):
        cue = self.message('/render/arena/cue/boss')
        self.rejects(cue)
        cue['args'][0]['value'] = 9.0
        self.rejects(cue, nested=True)

    def test_timeline_nested_bundle_is_validated(self):
        event = copy.deepcopy(next(e['message'] for e in self.examples
                              if e['message']['address'] == '/ui/arena/timeline/event'
                              and json.loads(e['message']['args'][0]['value'])['kind'] == 'event'))
        def mutate(p):
            p['bundle']['messages'] = [{'address': '/input/arena/start', 'args': []}]
        self.rejects(self.change_payload(event, mutate))

    def test_incomplete_variant_coverage_fails(self):
        for example in self.examples:
            if example['message']['address'] == '/game/arena/attack' and 'boss-burst' in example['name']:
                continue
            self.validator.message(example['message'], nested=example.get('context') == 'clip')
        with self.assertRaisesRegex(ValueError, 'variant coverage'):
            self.validator.complete()

    def test_doc_generation_preserves_prose_and_detects_stale_table(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'reference.md'
            path.write_text('Hand-written introduction\n' + contracts.BEGIN + '\nstale\n' + contracts.END + '\nTail\n')
            with self.assertRaisesRegex(ValueError, 'stale'):
                contracts.document(path=path)
            contracts.document(write=True, path=path)
            self.assertTrue(path.read_text().startswith('Hand-written introduction\n'))
            self.assertTrue(path.read_text().endswith('\nTail\n'))
            contracts.document(path=path)

    def test_source_catalog_and_examples_are_complete(self):
        contracts.source_coverage(self.validator.entries)
        for example in self.examples:
            self.validator.message(example['message'], nested=example.get('context') == 'clip')
        self.validator.complete()


if __name__ == '__main__':
    unittest.main()
