"""Bootstrap contract tests: real Git working copies and mocked external builds."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import shutil
import signal
import sys
import time
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from source_evidence import dependency_inputs


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


setup = module("demo_setup", "setup.py")
run = module("demo_run", "run.py")
REV = "a" * 40


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.demo = self.root / "demo"
        self.demo.mkdir()
        self.demo_manifest = ('[workspace]\nmembers = ["app"]\n[workspace.dependencies]\n'
            f'kitu-core = {{ git = "https://example.invalid/kitu", rev = "{REV}", default-features = false, features = ["example"] }}\n'
            f'kitu-runtime = {{ git = "https://example.invalid/kitu", rev = "{REV}" }}\n'
            'anyhow = "1"\n[profile.release]\nlto = true\n')
        (self.demo / "Cargo.toml").write_text(self.demo_manifest)
        (self.demo / "Cargo.lock").write_text("original lock\n")
        (self.demo / ".gitignore").write_text("/.kitu/\n/target/\n/node_modules/\n/unity/Library/\n")
        (self.demo / "deleted.txt").write_text("tracked and then deleted")
        (self.demo / "working.txt").write_text("original")
        self.git(self.demo, "init", "-q")
        self.git(self.demo, "add", ".")
        self.git(self.demo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        self.kitu = self.root / "kitu"
        self.kitu.mkdir()
        (self.kitu / "Cargo.toml").write_text('[workspace]\nmembers = ["crates/*"]\n')
        for name in ("kitu-core", "kitu-runtime"):
            path = self.kitu / "crates" / name
            path.mkdir(parents=True)
            (path / "Cargo.toml").write_text(f'[package]\nname = "{name}"\nversion = "0.1.0"\n')
        self.git(self.kitu, "init", "-q")
        self.git(self.kitu, "add", ".")
        self.git(self.kitu, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")

    def git(self, directory, *argv):
        return subprocess.check_output(["git", "-C", str(directory), *argv], stderr=subprocess.DEVNULL, text=True).strip()

    def test_pins_are_one_full_revision(self):
        names, _, revision = setup.pinned_dependencies(self.demo)
        self.assertEqual(set(names), {"kitu-core", "kitu-runtime"})
        self.assertEqual(revision, REV)
        for altered in (self.demo_manifest.replace(REV, "short", 1), self.demo_manifest.replace(REV, "b" * 40, 1)):
            (self.demo / "Cargo.toml").write_text(altered)
            with self.assertRaises(setup.SetupError):
                setup.pinned_dependencies(self.demo)

    def test_override_preserves_original_and_changes_only_kitu(self):
        dependencies, _, _ = setup.pinned_dependencies(self.demo)
        members = setup.kitu_members(self.kitu, dependencies)
        copied = setup.copy_working_demo(self.demo, os.environ.copy())
        setup.override_manifest(copied, members)
        actual = setup.document(copied / "Cargo.toml")
        self.assertEqual((self.demo / "Cargo.toml").read_text(), self.demo_manifest)
        self.assertEqual(actual["workspace"]["dependencies"]["anyhow"], "1")
        self.assertEqual(actual["profile"]["release"]["lto"], True)
        core = actual["workspace"]["dependencies"]["kitu-core"]
        self.assertEqual(core, {"path": str(members["kitu-core"]), "default-features": False, "features": ["example"]})
        self.assertEqual((copied / "Cargo.lock").read_text(), "original lock\n")
        self.assertIn("Cargo.toml", self.git(copied, "diff", "--name-only"))

    def test_copy_preserves_working_changes_without_generated_directories(self):
        (self.demo / "working.txt").write_text("edited")
        (self.demo / "deleted.txt").unlink()
        (self.demo / "new.txt").write_text("eligible untracked")
        for relative in ("target/cache", "node_modules/cache", "unity/Library/cache", ".kitu/overrides/old/Cargo.toml"):
            path = self.demo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("generated")
        first = setup.copy_working_demo(self.demo, os.environ.copy())
        second = setup.copy_working_demo(self.demo, os.environ.copy())
        self.assertNotEqual(first, second)
        self.assertEqual((first / "working.txt").read_text(), "edited")
        self.assertEqual((first / "new.txt").read_text(), "eligible untracked")
        self.assertFalse((first / "deleted.txt").exists())
        for relative in ("target", "node_modules", "unity/Library", ".kitu"):
            self.assertFalse((first / relative).exists())
        self.assertTrue((self.demo / ".kitu/overrides/old/Cargo.toml").exists())
        self.assertEqual(Path(self.git(first, "rev-parse", "--show-toplevel")), first)
        self.assertEqual(self.git(first, "rev-parse", "HEAD"), self.git(self.demo, "rev-parse", "HEAD"))
        self.assertIn("deleted.txt", self.git(first, "diff", "--name-only"))

    def test_clean_pin_rejected_but_dirty_override_allowed(self):
        revision, status = setup.source_revision(self.kitu, os.environ.copy(), require_clean=True)
        self.assertEqual(len(revision), 40)
        self.assertEqual(status, "")
        (self.kitu / "untracked.rs").write_text("changed")
        with self.assertRaisesRegex(setup.SetupError, "local changes"):
            setup.source_revision(self.kitu, os.environ.copy(), require_clean=True)
        self.assertIn("untracked.rs", setup.source_revision(self.kitu, os.environ.copy(), require_clean=False)[1])

    def test_effective_lock_diff_is_saved_only_in_copy(self):
        copy = setup.copy_working_demo(self.demo, os.environ.copy())
        (copy / "Cargo.lock").write_text("effective lock\n")
        path = Path(setup.save_diff(copy, "Cargo.lock", "original lock\n"))
        self.assertIn("-original lock", path.read_text())
        self.assertIn("+effective lock", path.read_text())
        self.assertEqual((self.demo / "Cargo.lock").read_text(), "original lock\n")

    def selection(self):
        copy = setup.copy_working_demo(self.demo, os.environ.copy())
        (copy / "app").mkdir()
        inputs = {"schema": 1, "app_root": str(copy / "app"), "roots": [
            {"logical": "kitu-core|0.1.0|path", "path": str(self.kitu / "crates/kitu-core")}]}
        setup.write_json(copy / "app/kitu-build-inputs.json", inputs)
        record = {"schema": 1, "mode": "override", "path": str(self.kitu), "effectiveDemoRoot": str(copy),
                  "originalDemoRoot": str(self.demo), "cargoHome": str(self.root / "cargo"),
                  "revision": self.git(self.kitu, "rev-parse", "HEAD"),
                  "kituPackages": [{"name": "kitu-core", "source": None}],
                  "dependencyInputs": dependency_inputs(copy)}
        setup.write_json(copy / ".kitu/source.json", record)
        setup.write_json(self.demo / ".kitu/source.json", record)
        return copy, record

    @unittest.skipUnless(os.name == "posix", "POSIX exec contract")
    def test_run_honors_effective_root_and_cargo_environment_without_shell(self):
        copy, record = self.selection()
        with mock.patch.object(run.os, "chdir") as change_directory, \
                mock.patch.object(run.os, "execvpe", side_effect=SystemExit(17)) as execute:
            with self.assertRaises(SystemExit) as result:
                run.main(["--", "command", "argument with spaces", "$(literal)"], self.demo)
            self.assertEqual(result.exception.code, 17)
            self.assertEqual(execute.call_args.args[0], "command")
            self.assertEqual(execute.call_args.args[1], ["command", "argument with spaces", "$(literal)"])
            change_directory.assert_called_once_with(copy)
            self.assertEqual(execute.call_args.args[2]["CARGO_HOME"], record["cargoHome"])
        with mock.patch.object(run.os, "chdir"), \
                mock.patch.object(run.os, "execvpe", side_effect=SystemExit(0)):
            with self.assertRaises(SystemExit) as result:
                run.main(["command"], self.demo)
            self.assertEqual(result.exception.code, 0)

    @unittest.skipUnless(os.name == "posix", "POSIX signal contract")
    def test_posix_runner_replaces_wrapper_and_does_not_survive_sigterm(self):
        self.selection()
        (self.demo / "tools").mkdir()
        shutil.copy2(TOOLS / "run.py", self.demo / "tools/run.py")
        shutil.copy2(TOOLS / "source_evidence.py", self.demo / "tools/source_evidence.py")
        ready, survived = self.root / "child.ready", self.root / "child.survived"
        child = ("import os,time; from pathlib import Path; "
                 f"Path({str(ready)!r}).write_text(str(os.getpid())); time.sleep(0.4); "
                 f"Path({str(survived)!r}).write_text('survived'); time.sleep(30)")
        process = subprocess.Popen([sys.executable, str(self.demo / "tools/run.py"),
                                    sys.executable, "-c", child], start_new_session=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(ready.exists(), "selected command did not start")
            self.assertEqual(int(ready.read_text()), process.pid)
            process.terminate()
            self.assertEqual(process.wait(timeout=3), -signal.SIGTERM)
            time.sleep(0.5)
            self.assertFalse(survived.exists())
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate(timeout=3)
        result = subprocess.run([sys.executable, str(self.demo / "tools/run.py"),
                                 sys.executable, "-c", "raise SystemExit(23)"], capture_output=True)
        self.assertEqual(result.returncode, 23)
        result = subprocess.run([sys.executable, str(self.demo / "tools/run.py"),
                                 "missing-demo-command-test"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Cannot run selected demo:", result.stderr)

    def test_run_rejects_stale_or_missing_selection(self):
        with self.assertRaisesRegex(ValueError, "setup.py first"):
            run.selected(self.demo)
        copy, record = self.selection()
        record["revision"] = "b" * 40
        setup.write_json(copy / ".kitu/source.json", record)
        with self.assertRaisesRegex(ValueError, "differs"):
            run.selected(self.demo)

    def test_dependency_repin_and_native_manifest_or_config_changes_require_setup(self):
        copy, _record = self.selection()
        for relative in ("Cargo.toml", "Cargo.lock", "app/native/Cargo.toml", ".cargo/config.toml", "admin/pnpm-lock.yaml"):
            with self.subTest(relative=relative):
                path = copy / relative
                before = path.read_bytes() if path.exists() else None
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((before or b"") + b"\n# changed dependency input\n")
                with self.assertRaisesRegex(ValueError, "dependency input changed"):
                    run.selected(self.demo)
                if before is None:
                    path.unlink()
                else:
                    path.write_bytes(before)

    def test_live_app_content_and_same_head_kitu_source_edits_remain_valid(self):
        copy, record = self.selection()
        for path in (copy / "app/src/lib.rs", copy / "app/content/arena.tmd", self.kitu / "crates/kitu-core/src/lib.rs"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("local authoring edit\n")
        selected, environment = run.selected(self.demo)
        self.assertEqual(selected, copy)
        self.assertEqual(environment["KITU_SOURCE_PATH"], record["path"])

    def test_prepared_graph_cannot_switch_to_another_root_or_origin(self):
        copy, _record = self.selection()
        path = copy / "app/kitu-build-inputs.json"
        original = json.loads(path.read_text())
        other = self.root / "another-kitu"
        other.mkdir()
        for field, value in (("path", str(other)), ("logical", "kitu-core|0.1.0|git+file:///other#" + REV)):
            inputs = json.loads(json.dumps(original))
            inputs["roots"][0][field] = value
            setup.write_json(path, inputs)
            with self.assertRaisesRegex(ValueError, "graph differs"):
                run.selected(self.demo)
    def test_native_and_app_dependencies_both_validate_requested_origin(self):
        packages = [
            {"id": "app", "name": "kitu-demo-game", "manifest_path": str(self.demo / "app/Cargo.toml")},
            {"id": "native", "name": "kitu-demo-game-native", "manifest_path": str(self.demo / "app/native/Cargo.toml")},
            {"id": "core", "name": "kitu-core", "manifest_path": str(self.kitu / "crates/kitu-core/Cargo.toml"), "source": None},
            {"id": "runtime", "name": "kitu-runtime", "manifest_path": str(self.kitu / "crates/kitu-runtime/Cargo.toml"), "source": None}]
        metadata = {"packages": packages, "workspace_members": ["app", "native"], "resolve": {"nodes": [
            {"id": "app", "deps": [{"pkg": "core"}]}, {"id": "native", "deps": [{"pkg": "runtime"}]},
            {"id": "core", "deps": []}, {"id": "runtime", "deps": []}]}}
        preparer = module("fixture_prepare", "prepare-kitu-build.py")
        with mock.patch.object(setup, "load_preparer", return_value=preparer):
            source, selected = setup.resolved_source(self.demo, metadata, self.kitu)
            self.assertEqual(source, self.kitu)
            self.assertEqual({p["name"] for p in selected}, {"kitu-core", "kitu-runtime"})
            packages[-1]["source"] = "git+https://different.invalid/kitu#" + REV
            with self.assertRaisesRegex(setup.SetupError, "mixed Kitu"):
                setup.resolved_source(self.demo, metadata, self.kitu)


if __name__ == "__main__":
    unittest.main()
