"""Source evidence survives discarded override checkouts; no compiler required."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from source_evidence import capture_graph, capture_source, dependency_inputs


class SourceEvidenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "demo/.kitu/overrides/demo-selected"
        self.source = self.base / "kitu"
        self.evidence = self.base / "evidence"
        for path in (self.root / ".kitu", self.root / "app", self.root / "admin", self.source):
            path.mkdir(parents=True)
        self.git("init", "-q")
        (self.source / "Cargo.toml").write_text("# fixture\n")
        (self.source / "lib.rs").write_text("// original\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
        self.revision = self.git("rev-parse", "HEAD").strip()
        (self.source / "lib.rs").write_text("// local edit at same HEAD\n")
        (self.root / "Cargo.lock").write_text("effective cargo lock\n")
        (self.root / "admin/pnpm-lock.yaml").write_text("effective pnpm lock\n")
        self.selection = {"schema": 1, "mode": "override", "path": str(self.source),
                          "revision": self.revision, "effectiveDemoRoot": str(self.root),
                          "kituPackages": [{"name": "kitu-core", "source": None}],
                          "overrideLockDiff": str(self.root / ".kitu/Cargo.lock.diff"),
                          "overridePnpmLockDiff": str(self.root / ".kitu/admin-pnpm-lock.yaml.diff")}
        for field in ("overrideLockDiff", "overridePnpmLockDiff"):
            Path(self.selection[field]).write_text("--- original\n+++ effective\n")
        self.write_selection()
        self.inputs = {"schema": 1, "app_root": str(self.root / "app"), "target": "fixture-target",
                       "features": [], "graph": [{"package": "kitu-core|0.1.0|path", "features": []}],
                       "roots": [{"logical": "kitu-core|0.1.0|path", "path": str(self.source)}],
                       "guards": [{"path": "private-config"}], "build_configuration": {"private": "config"}}
        self.write_inputs()
        self.selection["dependencyInputs"] = dependency_inputs(self.root)
        self.write_selection()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.source), *args], text=True)

    def write_selection(self):
        (self.root / ".kitu/source.json").write_text(json.dumps(self.selection))

    def write_inputs(self):
        (self.root / "app/kitu-build-inputs.json").write_text(json.dumps(self.inputs))

    def test_effective_lock_diff_and_source_identities_survive_checkout_removal(self):
        result = capture_source(self.root, self.evidence)
        self.assertEqual((result["mode"], result["revision"]), ("override", self.revision))
        paths = [result["selection"], result["kitu"], *result["locks"].values(),
                 *result["lockDiffs"].values(), *result["graphs"].values()]
        shutil.rmtree(self.base / "demo")
        shutil.rmtree(self.source)
        for reference in paths:
            self.assertFalse(Path(reference["path"]).is_absolute())
            self.assertEqual((self.evidence / reference["path"]).stat().st_size, reference["size"])
        lock = json.loads((self.evidence / result["locks"]["cargo"]["path"]).read_text())
        self.assertEqual(lock["sourceLabel"], "Cargo.lock")
        self.assertEqual(lock["size"], len("effective cargo lock\n"))
        source = json.loads((self.evidence / result["kitu"]["path"]).read_text())
        self.assertTrue(source["dirty"])
        self.assertEqual(len(source["dirtyFilesSha256"]), 64)
        self.assertEqual(source["packages"], ["kitu-core"])
        for path in (self.evidence / "source").iterdir():
            text = path.read_text()
            for private in (str(self.base), "effective cargo lock", "effective pnpm lock", "--- original", "private-config"):
                self.assertNotIn(private, text)

    def test_graph_snapshots_preserve_scope_features_and_omit_unrelated_configuration(self):
        first = capture_graph(self.root, self.evidence, "initial")
        self.inputs["features"] = ["inspection"]
        self.write_inputs()
        second = capture_graph(self.root, self.evidence, "clippy")
        original = json.loads((self.evidence / first["path"]).read_text())
        updated = json.loads((self.evidence / second["path"]).read_text())
        self.assertEqual(original["features"], [])
        self.assertEqual(updated["features"], ["inspection"])
        self.assertNotIn("guards", updated)
        self.assertNotIn("build_configuration", updated)
        self.assertEqual(updated["sourceLabels"], ["package/kitu-core"])
        self.assertEqual(len(updated["graphSha256"]), 64)

    def test_wrong_effective_root_or_changed_head_is_rejected(self):
        self.selection["effectiveDemoRoot"] = str(self.base)
        self.write_selection()
        with self.assertRaisesRegex(ValueError, "tools/run.py"):
            capture_source(self.root, self.evidence)
        self.selection["effectiveDemoRoot"] = str(self.root)
        self.selection["revision"] = "a" * 40
        self.write_selection()
        with self.assertRaisesRegex(ValueError, "HEAD changed"):
            capture_source(self.root, self.evidence)

    def test_external_diff_and_foreign_graph_are_rejected(self):
        outside = self.base / "unrelated.diff"
        outside.write_text("unrelated")
        self.selection["overrideLockDiff"] = str(outside)
        self.write_selection()
        with self.assertRaisesRegex(ValueError, "outside"):
            capture_source(self.root, self.evidence)
        self.inputs["app_root"] = str(self.base)
        self.write_inputs()
        with self.assertRaisesRegex(ValueError, "another demo"):
            capture_graph(self.root, self.evidence, "test")

    def test_pinned_rust_only_has_explicitly_absent_diffs_and_allows_cargo_marker(self):
        self.git("checkout", "--", "lib.rs")
        (self.source / ".cargo-ok").write_text("cargo marker")
        # Default setup's Cargo cache is below the demo, but these are still
        # dependency sources, not app workspace packages exempt from matching.
        cached = self.root / ".kitu/cargo/git/checkout"
        shutil.copytree(self.source, cached)
        self.source = cached
        self.selection["path"] = str(cached)
        self.inputs["roots"][0]["path"] = str(cached)
        self.selection.update(mode="pinned", overrideLockDiff=None, overridePnpmLockDiff=None)
        origin = "git+https://example.invalid/kitu?rev=" + self.revision + "#" + self.revision
        self.selection["kituPackages"][0]["source"] = origin
        self.inputs["roots"][0]["logical"] = "kitu-core|0.1.0|" + origin
        self.write_inputs()
        self.write_selection()
        result = capture_source(self.root, self.evidence)
        self.assertEqual(result["lockDiffs"], {"cargo": None, "pnpm": None})
        self.assertFalse(json.loads((self.evidence / result["kitu"]["path"]).read_text())["dirty"])

    def test_changed_graph_source_cannot_claim_selected_revision(self):
        foreign = self.base / "foreign-kitu"
        foreign.mkdir()
        self.inputs["roots"][0]["path"] = str(foreign)
        self.write_inputs()
        with self.assertRaisesRegex(ValueError, "graph differs"):
            capture_graph(self.root, self.evidence, "test")
        self.assertFalse(self.evidence.exists())

    @unittest.skipIf(sys.platform == "win32", "native coordinator requires fcntl")
    def test_native_preflight_retains_selection_before_sdk_failure_and_cargo_graph_before_build(self):
        spec = importlib.util.spec_from_file_location("source_evidence_native", TOOLS / "verify-arena-macos.py")
        native = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(native)
        args = argparse.Namespace(evidence=self.evidence, scope="native", cargo="cargo", profile="dev", editor=None, port=None)
        verification = native.Verification(args)
        with patch.object(native, "ROOT", self.root), patch.object(native, "require_macos", side_effect=RuntimeError("SDK unavailable")):
            with self.assertRaisesRegex(RuntimeError, "SDK unavailable"):
                verification.preflight()
        report = json.loads((self.evidence / "verification.json").read_text())
        self.assertTrue((self.evidence / report["dependencySource"]["selection"]["path"]).is_file())
        verification.target = self.base / "target/triple/debug"
        calls = []

        def command(argv, **kwargs):
            calls.append(argv)
            verification.command_id += 1
            if len(calls) == 1:
                self.inputs["target"] = native.TARGET
                self.write_inputs()
            else:
                graph = verification.report["dependencySource"]["graphs"]["command-001"]
                self.assertEqual(json.loads((self.evidence / graph["path"]).read_text())["target"], native.TARGET)
            return "fixture success"

        with patch.object(native, "ROOT", self.root), patch.object(native, "APP", self.root / "app"), patch.object(verification, "command", side_effect=command):
            verification.cargo("test", "-p", "kitu-demo-game-native")
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
