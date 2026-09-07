#!/usr/bin/env python3
"""Run a command in the demo selected by tools/setup.py."""
import sys

if sys.version_info < (3, 11):
    raise SystemExit("run requires Python 3.11 or newer")

import json
import os
from pathlib import Path
import subprocess
from source_evidence import validate_dependency_selection, validate_graph_selection

ROOT = Path(__file__).resolve().parents[1]


def selected(root):
    location = root / ".kitu" / "source.json"
    if not location.is_file():
        raise ValueError("run tools/setup.py first to select a pinned or local Kitu dependency")
    record = json.loads(location.read_text(encoding="utf-8"))
    if record.get("schema") != 1 or record.get("mode") not in ("pinned", "override"):
        raise ValueError("invalid source selection; rerun tools/setup.py")
    original = Path(record["originalDemoRoot"]).resolve(strict=True)
    effective = Path(record["effectiveDemoRoot"]).resolve(strict=True)
    if root.resolve() not in (original, effective):
        raise ValueError("source selection belongs to another demo")
    if record["mode"] == "pinned" and effective != original:
        raise ValueError("pinned selection must use the original demo")
    if record["mode"] == "override" and not effective.is_relative_to(original / ".kitu" / "overrides"):
        raise ValueError("override selection is outside its temporary checkout directory")
    if not (effective / ".git").exists():
        raise ValueError("effective demo Git checkout is missing; rerun tools/setup.py")
    canonical = effective / ".kitu" / "source.json"
    if not canonical.is_file() or json.loads(canonical.read_text(encoding="utf-8")) != record:
        raise ValueError("source selection differs from its effective demo; rerun tools/setup.py")
    source = Path(record["path"]).resolve(strict=True)
    if not (effective / "Cargo.toml").is_file() or not (source / "Cargo.toml").is_file():
        raise ValueError("selected demo or Kitu source is missing; rerun tools/setup.py")
    validate_dependency_selection(effective, record)
    inputs = json.loads((effective / "app/kitu-build-inputs.json").read_text(encoding="utf-8"))
    validate_graph_selection(effective, record, inputs)
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if revision != record["revision"]:
        raise ValueError("selected Kitu revision changed; rerun tools/setup.py")
    if record["mode"] == "pinned":
        status = subprocess.check_output(["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all"], text=True)
        if any(line != "?? .cargo-ok" for line in status.splitlines()):
            raise ValueError("pinned Kitu source has local changes; use --kitu-path for local development")
    environment = os.environ.copy()
    environment["CARGO_HOME"] = record["cargoHome"]
    environment["KITU_SOURCE_PATH"] = str(source)
    environment["KITU_OSC_IR_WASM_CRATE"] = str(source / "crates" / "kitu-osc-ir-wasm")
    environment["KITU_ADMIN_WASM_OUT_DIR"] = str(effective / "admin" / "static" / "kitu-osc-ir-wasm")
    return effective, environment


def main(argv=None, root=ROOT):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--"]:
        argv.pop(0)
    if not argv:
        print("usage: python3 tools/run.py [--] COMMAND [ARG ...]", file=sys.stderr)
        return 2
    try:
        directory, environment = selected(root)
        if os.name == "posix":
            # Keep the command at this PID so cancellation reaches the actual
            # verifier/server, including its owned-child cleanup handlers.
            os.chdir(directory)
            os.execvpe(argv[0], argv, environment)
        else:
            return subprocess.run(argv, cwd=directory, env=environment).returncode
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Cannot run selected demo: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
