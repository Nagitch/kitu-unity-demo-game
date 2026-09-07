"""Retain dependency identities without exposing local paths or raw lock diffs."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_identity(path, label):
    data = path.read_bytes()
    return {"sourceLabel": label, "sha256": digest(data), "size": len(data)}


def dependency_inputs(root, manifests=(), cargo_home=None):
    """Bind setup to dependency declarations, while allowing source/content edits."""
    paths = {root / name for name in ("Cargo.toml", "Cargo.lock", "app/Cargo.toml",
             "app/native/Cargo.toml", "admin/package.json", "admin/pnpm-lock.yaml")}
    paths.update(Path(path) for path in manifests)
    directories = [root, *root.parents]
    for directory in directories:
        paths.update(directory / ".cargo" / name for name in ("config", "config.toml"))
    if cargo_home is not None:
        paths.update(Path(cargo_home) / name for name in ("config", "config.toml"))
    return [{"path": str(path.resolve()), "sha256": digest(path.read_bytes()) if path.is_file() else None}
            for path in sorted(paths)]


def validate_dependency_selection(root, selection):
    inputs = selection.get("dependencyInputs")
    if not isinstance(inputs, list) or not inputs:
        raise ValueError("source selection lacks dependency bindings; rerun tools/setup.py")
    required = {str((root / name).resolve()) for name in
                ("Cargo.toml", "Cargo.lock", "app/Cargo.toml", "app/native/Cargo.toml",
                 "admin/package.json", "admin/pnpm-lock.yaml")}
    if not required.issubset({row["path"] for row in inputs}):
        raise ValueError("source selection lacks dependency manifests; rerun tools/setup.py")
    for row in inputs:
        path = Path(row["path"])
        actual = digest(path.read_bytes()) if path.is_file() else None
        if actual != row["sha256"]:
            raise ValueError(f"selected dependency input changed: {path}; rerun tools/setup.py")


def validate_graph_selection(root, selection, inputs):
    if inputs.get("schema") != 1 or Path(inputs["app_root"]).resolve() != (root / "app").resolve():
        raise ValueError("prepared graph belongs to another demo; rerun preparation")
    source = Path(selection["path"]).resolve(strict=True)
    origins = {package.get("source") or "path" for package in selection["kituPackages"]}
    expected_origin = "path" if selection["mode"] == "override" else next(iter(origins), None)
    if origins != {expected_origin} or (selection["mode"] == "pinned" and
            (not expected_origin.startswith("git+") or not expected_origin.endswith("#" + selection["revision"]))):
        raise ValueError("invalid selected Kitu origin; rerun tools/setup.py")
    found = False
    for package in inputs["roots"]:
        name, _version, origin = package["logical"].split("|", 2)
        path = Path(package["path"]).resolve(strict=True)
        demo_package = (name, path) in {
            ("kitu-demo-game", (root / "app").resolve()),
            ("kitu-demo-game-native", (root / "app/native").resolve()),
        }
        if not name.startswith("kitu-") or demo_package:
            continue  # App/native workspace packages belong to the demo.
        found = True
        if not path.is_relative_to(source) or origin != expected_origin:
            raise ValueError("prepared Kitu graph differs from selected source; rerun tools/setup.py")
    if not found:
        raise ValueError("prepared graph has no selected Kitu sources")


def retain(evidence, name, data):
    path = evidence / "source" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"path": path.relative_to(evidence).as_posix(),
            "sha256": digest(data), "size": len(data)}


def retain_json(evidence, name, value):
    return retain(evidence, name, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode())


def capture_graph(root, evidence, label):
    if not re.fullmatch(r"[a-z0-9-]+", label):
        raise ValueError("invalid source evidence graph label")
    inputs = json.loads((root / "app/kitu-build-inputs.json").read_text())
    selection = json.loads((root / ".kitu/source.json").read_text())
    validate_dependency_selection(root, selection)
    validate_graph_selection(root, selection, inputs)
    # Evidence is uploaded by existing CI jobs. Package source IDs, absolute
    # roots, configs and raw locks can expose private checkout information.
    graph = {key: inputs[key] for key in ("schema", "target", "features")}
    graph["graphSha256"] = digest(json.dumps(inputs["graph"], sort_keys=True, separators=(",", ":")).encode())
    graph["packages"] = sorted({row["package"].split("|", 1)[0] for row in inputs["graph"]})
    graph["sourceLabels"] = sorted({"package/" + row["logical"].split("|", 1)[0] for row in inputs["roots"]})
    return retain_json(evidence, "resolved-graph-" + label + ".json", graph)


def capture_source(root, evidence):
    root = root.resolve(strict=True)
    raw = (root / ".kitu/source.json").read_bytes()
    selection = json.loads(raw)
    if selection.get("schema") != 1 or selection.get("mode") not in ("pinned", "override"):
        raise ValueError("invalid Kitu source selection; rerun setup")
    if Path(selection["effectiveDemoRoot"]).resolve() != root:
        raise ValueError("verification must run in the effective demo; use tools/run.py")
    validate_dependency_selection(root, selection)
    source = Path(selection["path"]).resolve(strict=True)

    def git(*args):
        return subprocess.check_output(["git", "-C", str(source), *args])

    revision = git("rev-parse", "HEAD").decode().strip()
    if revision != selection["revision"]:
        raise ValueError("selected Kitu HEAD changed; rerun setup")
    paths = set(git("diff", "--name-only", "-z", "HEAD").split(b"\0"))
    paths.update(git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0"))
    dirty = []
    for raw_path in sorted(paths - {b"", b".cargo-ok"}):
        name = os.fsdecode(raw_path)
        path = source / name
        data = path.read_bytes() if path.is_file() else None
        dirty.append({"path": name, "sha256": digest(data) if data is not None else None,
                      "size": len(data) if data is not None else None})
    if selection["mode"] == "pinned" and dirty:
        raise ValueError("pinned Kitu source has local changes; use an override")
    public_selection = {"schema": 1, "revision": revision, "mode": selection["mode"],
                        "sourceLabel": "selected-kitu", "demoLabel": "effective-demo"}
    result = {"revision": revision, "mode": selection["mode"],
              "selection": retain_json(evidence, "selection.json", public_selection),
              "kitu": retain_json(evidence, "kitu.json", {
                  **public_selection, "dirty": bool(dirty),
                  "dirtyFilesSha256": digest(json.dumps(dirty, sort_keys=True, separators=(",", ":")).encode()),
                  "packages": sorted({package["name"] for package in selection["kituPackages"]})}),
              "locks": {}, "lockDiffs": {},
              "graphs": {"initial": capture_graph(root, evidence, "initial")}}
    for key, relative, name in (("cargo", "Cargo.lock", "Cargo.lock"),
                                ("pnpm", "admin/pnpm-lock.yaml", "admin-pnpm-lock.yaml")):
        result["locks"][key] = retain_json(evidence, name + ".json", file_identity(root / relative, relative))
    for key, field, name in (("cargo", "overrideLockDiff", "Cargo.lock.diff"),
                             ("pnpm", "overridePnpmLockDiff", "admin-pnpm-lock.yaml.diff")):
        selected = selection.get(field)
        if selected is None:
            result["lockDiffs"][key] = None
            continue
        path = Path(selected).resolve(strict=True)
        if not path.is_relative_to(root / ".kitu"):
            raise ValueError("selected lock diff is outside the effective demo cache")
        result["lockDiffs"][key] = retain_json(evidence, name + ".json", file_identity(path, ".kitu/" + name))
    return result
