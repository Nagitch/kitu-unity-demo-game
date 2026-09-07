"""Real Cargo/Git setup round-trip using tiny local crates and no registry deps.

Opt in with KITU_SETUP_CARGO_INTEGRATION=1 and Rust/Cargo 1.96.0 on PATH.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
from source_evidence import capture_graph


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, TOOLS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


setup = load("cargo_fixture_setup", "setup.py")
run = load("cargo_fixture_run", "run.py")


@unittest.skipUnless(os.environ.get("KITU_SETUP_CARGO_INTEGRATION") == "1", "opt-in real Cargo setup test")
class CargoSetupTests(unittest.TestCase):
    def test_pinned_override_and_reset_share_actual_resolved_sources(self):
        with tempfile.TemporaryDirectory(prefix="demo-setup-cargo-") as temporary:
            root = Path(temporary).resolve()
            source, demo = root / "source", root / "demo"
            source.mkdir()
            demo.mkdir()
            def git(directory, *argv):
                return subprocess.check_output(["git", "-C", str(directory), *argv], text=True, stderr=subprocess.DEVNULL).strip()
            def commit(directory):
                git(directory, "init", "-q")
                git(directory, "add", ".")
                git(directory, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
            names = ["kitu-core", "kitu-runtime", "kitu-unity-ffi"]
            (source / "Cargo.toml").write_text('[workspace]\nmembers = ["crates/*"]\nresolver = "2"\n')
            for name in names:
                crate = source / "crates" / name
                (crate / "src").mkdir(parents=True)
                (crate / "Cargo.toml").write_text(f'[package]\nname = "{name}"\nversion = "0.1.0"\nedition = "2021"\n')
                (crate / "src/lib.rs").write_text("pub const EXAMPLE: u8 = 1;\n")
            commit(source)
            revision = git(source, "rev-parse", "HEAD")
            (demo / "Cargo.toml").write_text('[workspace]\nmembers = ["app", "app/native"]\nresolver = "2"\n[workspace.dependencies]\n' + ''.join(
                f'{name} = {{ git = "{source.as_uri()}", rev = "{revision}" }}\n' for name in names))
            (demo / ".gitignore").write_text('/.kitu/\n/app/kitu-build-inputs.json\n**/__pycache__/\n')
            for name, relative, dependencies in [("kitu-demo-game", "app", names[:2]), ("kitu-demo-game-native", "app/native", names[2:])]:
                crate = demo / relative
                (crate / "src").mkdir(parents=True)
                (crate / "src/lib.rs").write_text("pub fn example() {}\n")
                (crate / "Cargo.toml").write_text(f'[package]\nname = "{name}"\nversion = "0.1.0"\nedition = "2021"\n[dependencies]\n' + ''.join(
                    f'{dependency} = {{ workspace = true }}\n' for dependency in dependencies))
            (demo / "tools").mkdir()
            for filename in ("setup.py", "run.py", "prepare-kitu-build.py", "source_evidence.py"):
                shutil.copy2(TOOLS / filename, demo / "tools" / filename)
            shutil.copy2(TOOLS.parent / "rust-toolchain.toml", demo / "rust-toolchain.toml")
            args = argparse.Namespace(kitu_path=None, rust_only=True, cargo=shutil.which("cargo"), rustc=shutil.which("rustc"), node="node", pnpm="pnpm")
            with mock.patch.dict(os.environ, {"CARGO_HOME": str(root / "cargo"), "CARGO_NET_OFFLINE": "false"}):
                subprocess.run([args.cargo, "generate-lockfile", "--manifest-path", str(demo / "Cargo.toml")], check=True, cwd=demo)
                commit(demo)
                manifest, lock = (demo / "Cargo.toml").read_bytes(), (demo / "Cargo.lock").read_bytes()
                pinned = setup.setup(args, demo)
                self.assertEqual(pinned["revision"], revision)
                self.assertEqual(pinned["mode"], "pinned")
                self.assertNotEqual(pinned["path"], str(source))
                self.assertTrue(Path(pinned["path"]).is_relative_to(root / "cargo"))
                self.assertEqual({p["name"] for p in pinned["kituPackages"]}, set(names))
                (source / "crates/kitu-core/src/lib.rs").write_text("pub const EXAMPLE: u8 = 2;\n")
                (demo / "working-note.txt").write_text("untracked authoring change")
                args.kitu_path = source
                overridden = setup.setup(args, demo)
                effective = Path(overridden["effectiveDemoRoot"])
                self.assertEqual(overridden["path"], str(source))
                self.assertIn("crates/kitu-core/src/lib.rs", overridden["sourceStatus"])
                self.assertEqual(Path(git(effective, "rev-parse", "--show-toplevel")), effective)
                self.assertIn("Cargo.toml", git(effective, "diff", "--name-only"))
                self.assertIn("Cargo.lock", git(effective, "diff", "--name-only"))
                self.assertEqual((effective / "working-note.txt").read_text(), "untracked authoring change")
                self.assertTrue(Path(overridden["overrideLockDiff"]).read_text())
                self.assertEqual((demo / "Cargo.toml").read_bytes(), manifest)
                self.assertEqual((demo / "Cargo.lock").read_bytes(), lock)

                self.assertEqual(subprocess.run([sys.executable, str(demo / "tools/run.py"), sys.executable, "-c", "from pathlib import Path; Path('selection-probe.txt').write_text(str(Path.cwd()))"]).returncode, 0)
                self.assertEqual((effective / "selection-probe.txt").read_text(), str(effective))
                self.assertFalse((demo / "selection-probe.txt").exists())
                args.kitu_path = None
                reset = setup.setup(args, demo)
                self.assertEqual(reset["mode"], "pinned")
                self.assertEqual(reset["effectiveDemoRoot"], str(demo))
                self.assertTrue(effective.is_dir())
                self.assertEqual(json.loads((demo / ".kitu/source.json").read_text())["effectiveDemoRoot"], str(demo))
                self.assertEqual((demo / "Cargo.toml").read_bytes(), manifest)
                self.assertEqual((demo / "Cargo.lock").read_bytes(), lock)

                # A real repin+lock regeneration must not leave Admin/source
                # selection on A while a subsequent preparation resolves B.
                commit(source)
                new_revision = git(source, "rev-parse", "HEAD")
                self.assertNotEqual(new_revision, revision)
                (demo / "Cargo.toml").write_bytes(manifest.replace(revision.encode(), new_revision.encode()))
                subprocess.run([args.cargo, "generate-lockfile", "--manifest-path", str(demo / "Cargo.toml")], check=True, cwd=demo)
                with self.assertRaisesRegex(ValueError, "dependency input changed"):
                    run.selected(demo)
                subprocess.run([sys.executable, demo / "tools/prepare-kitu-build.py", "--manifest-path", demo / "app/Cargo.toml"], check=True, cwd=demo)
                with self.assertRaisesRegex(ValueError, "dependency input changed"):
                    capture_graph(demo, root / "stale-evidence", "test")
                self.assertFalse((root / "stale-evidence").exists())
                refreshed = setup.setup(args, demo)
                self.assertEqual(refreshed["revision"], new_revision)
                self.assertEqual(run.selected(demo)[0], demo)


if __name__ == "__main__":
    unittest.main()
