#!/usr/bin/env python3
"""Prepare the pinned demo, or an isolated demo copy using a local Kitu checkout."""
import sys

if sys.version_info < (3, 11):
    raise SystemExit("setup requires Python 3.11 or newer; run python3.11 tools/setup.py")

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
from source_evidence import dependency_inputs, validate_graph_selection

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".kitu", "target", "node_modules", "Library", "Temp", "Obj", "Logs", "Builds", "UserSettings", "__pycache__", ".venv", ".arena"}
EXCLUDED_NAMES = {"kitu-build-inputs.json", "kitu-build-inputs.json.tmp"}


class SetupError(RuntimeError):
    pass


def command(argv, cwd, env, capture=False):
    result = subprocess.run([str(value) for value in argv], cwd=cwd, env=env, check=True,
                            stdout=subprocess.PIPE if capture else None, text=True)
    return result.stdout.strip() if capture else None


def document(path):
    return tomllib.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_dependencies(root):
    dependencies = {name: value for name, value in document(root / "Cargo.toml").get("workspace", {}).get("dependencies", {}).items()
                    if name.startswith("kitu-")}
    if not dependencies:
        raise SetupError("Cargo.toml declares no workspace Kitu dependencies")
    pins = set()
    for name, dependency in dependencies.items():
        if (not isinstance(dependency, dict) or "git" not in dependency or
                not re.fullmatch(r"[0-9a-f]{40}", dependency.get("rev", "")) or
                any(key in dependency for key in ("path", "branch", "tag"))):
            raise SetupError(f"{name} must use a git dependency pinned to one full 40-character revision")
        pins.add((dependency["git"], dependency["rev"]))
    if len(pins) != 1:
        raise SetupError("all Kitu dependencies must use the same repository and full revision")
    url, revision = pins.pop()
    return dependencies, url, revision


def kitu_members(source, names):
    manifest = document(source / "Cargo.toml")
    result = {}
    for pattern in manifest.get("workspace", {}).get("members", []):
        for member in source.glob(pattern):
            path = member / "Cargo.toml"
            if not path.is_file():
                continue
            name = document(path).get("package", {}).get("name")
            if name in names:
                if name in result:
                    raise SetupError(f"duplicate Kitu workspace package {name}")
                resolved = member.resolve(strict=True)
                if not resolved.is_relative_to(source):
                    raise SetupError(f"Kitu member {name} escapes its source root")
                result[name] = resolved
    missing = set(names) - set(result)
    if missing:
        raise SetupError(f"Kitu checkout is missing workspace packages: {', '.join(sorted(missing))}")
    return result


def override_manifest(root, members):
    """Edit only declared Kitu dependency entries; preserve the rest of TOML."""
    path = root / "Cargo.toml"
    content = path.read_text(encoding="utf-8")
    section = re.search(r"(?ms)^\[workspace\.dependencies\]\s*\n(.*?)(?=^\[|\Z)", content)
    if not section:
        raise SetupError("missing workspace.dependencies section")
    body = section.group(1)
    for name, source in sorted(members.items()):
        # The checked-in contract intentionally uses one inline table per Kitu
        # dependency, keeping substitutions explicit and reviewable.
        pattern = rf"(?m)^{re.escape(name)}[ \t]*=[ \t]*\{{[^\n]*\}}[ \t]*$"
        original = document(path)["workspace"]["dependencies"][name]
        retained = {key: value for key, value in original.items() if key not in {"git", "rev"}}
        fields = [f"path = {json.dumps(str(source))}"]
        for key, value in retained.items():
            fields.append(f"{key} = {json.dumps(value)}")
        body, count = re.subn(pattern, lambda _: f"{name} = {{ {', '.join(fields)} }}", body)
        if count != 1:
            raise SetupError(f"expected one inline workspace dependency for {name}")
    updated = content[:section.start(1)] + body + content[section.end(1):]
    tomllib.loads(updated)
    path.write_text(updated, encoding="utf-8")


def copy_working_demo(root, env):
    listed = subprocess.check_output(["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"], env=env)
    overrides = root / ".kitu" / "overrides"
    overrides.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix="demo-", dir=overrides)).resolve()
    try:
        # Keep an independent HEAD/index: verification in the copied tree must
        # report its effective Cargo/lock changes, never discover the parent Git.
        original_head = command(["git", "rev-parse", "HEAD"], root, env, capture=True)
        command(["git", "clone", "--quiet", "--local", "--no-hardlinks", "--no-checkout", root, destination], root, env)
        command(["git", "update-ref", "--no-deref", "HEAD", original_head], destination, env)
        command(["git", "read-tree", "HEAD"], destination, env)
        for raw in sorted(set(listed.split(b"\0")) - {b""}):
            relative = Path(os.fsdecode(raw))
            if relative.is_absolute() or ".." in relative.parts:
                raise SetupError("git returned an invalid working-tree path")
            if set(relative.parts) & EXCLUDED_PARTS or relative.name in EXCLUDED_NAMES:
                continue
            source = root / relative
            if not source.exists() and not source.is_symlink():
                continue  # Preserve working-tree deletions of tracked files.
            if source.is_dir() and not source.is_symlink():
                raise SetupError(f"nested repositories/submodules are not valid demo copy inputs: {relative}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_symlink():
                target.symlink_to(os.readlink(source))
            else:
                shutil.copy2(source, target)
    except Exception:
        print(f"Incomplete override copy retained for inspection: {destination}", file=sys.stderr)
        raise
    return destination


def source_revision(source, env, require_clean):
    actual = Path(command(["git", "rev-parse", "--show-toplevel"], source, env, capture=True)).resolve()
    if actual != source:
        raise SetupError(f"Kitu path must be the Git repository root: {source} (actual {actual})")
    revision = command(["git", "rev-parse", "HEAD"], source, env, capture=True)
    status = command(["git", "status", "--porcelain", "--untracked-files=all"], source, env, capture=True)
    # Cargo adds this untracked, empty checkout-completion marker itself.
    status = "\n".join(line for line in status.splitlines() if line != "?? .cargo-ok")
    if require_clean and status:
        raise SetupError(f"pinned Kitu checkout has local changes: {source}; use a clean cache or explicit --kitu-path")
    return revision, status


def load_preparer(root):
    specification = importlib.util.spec_from_file_location("kitu_prepare_inputs", root / "tools" / "prepare-kitu-build.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def resolve(root, cargo, env, target, locked=True):
    argv = [cargo, "metadata", "--format-version", "1", "--manifest-path", root / "app" / "Cargo.toml", "--filter-platform", target]
    if locked:
        argv.append("--locked")
    return json.loads(command(argv, root, env, capture=True))


def resolved_source(root, metadata, requested=None):
    preparer = load_preparer(root)
    app_path = (root / "app" / "Cargo.toml").resolve()
    app = next(package for package in metadata["packages"] if Path(package["manifest_path"]).resolve() == app_path)
    members = set(metadata.get("workspace_members", [app["id"]]))
    selected = set()
    for package in metadata["packages"]:
        if package["id"] in members:
            _, closure = preparer.reachable(metadata, package)
            selected.update(closure)
    packages = [package for package in metadata["packages"] if package["id"] in selected
                and package["name"].startswith("kitu-") and package["id"] not in members]
    if len({package.get("source") for package in packages}) != 1:
        raise SetupError("resolved workspace has mixed Kitu package origins")
    roots = {preparer.workspace_for(Path(package["manifest_path"]).resolve()).parent for package in packages}
    if len(roots) != 1:
        raise SetupError("resolved Kitu packages do not share exactly one source root")
    source = roots.pop()
    if requested is not None and source != requested:
        raise SetupError(f"Cargo resolved {source}, expected requested Kitu source {requested}")
    return source, packages


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_diff(root, relative, before):
    after = (root / relative).read_text(encoding="utf-8")
    diff = "".join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                       fromfile=f"original/{relative}", tofile=f"effective/{relative}"))
    output = root / ".kitu" / (relative.replace("/", "-") + ".diff")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(diff, encoding="utf-8")
    return str(output)


def check_versions(args, root, env):
    version = command([args.rustc, "--version"], root, env, capture=True)
    cargo_version = command([args.cargo, "--version"], root, env, capture=True)
    if not version.startswith("rustc 1.96.0 ") or not cargo_version.startswith("cargo 1.96.0 "):
        raise SetupError("Rust and Cargo 1.96.0 are required; install the repository rust-toolchain.toml toolchain with rustup")
    if not args.rust_only:
        if not command([args.node, "--version"], root, env, capture=True).startswith("v24."):
            raise SetupError("Node.js 24 is required for Admin setup")
        if command([args.pnpm, "--version"], root, env, capture=True) != "11.9.0":
            raise SetupError("pnpm 11.9.0 is required for Admin setup")
    verbose = command([args.rustc, "-vV"], root, env, capture=True)
    return next(line.removeprefix("host: ") for line in verbose.splitlines() if line.startswith("host: "))


def build_admin(root, source, args, env, override):
    env = dict(env, KITU_SOURCE_PATH=str(source),
               KITU_OSC_IR_WASM_CRATE=str(source / "crates" / "kitu-osc-ir-wasm"),
               KITU_ADMIN_WASM_OUT_DIR=str(root / "admin" / "static" / "kitu-osc-ir-wasm"))
    package = source / "tools" / "kitu-web-admin" / "package"
    for argv in (["install", "--frozen-lockfile"], ["run", "check"], ["run", "test"], ["run", "build"]):
        command([args.pnpm, "--dir", package, *argv], root, env)
    destination = root / ".kitu" / "admin-package"
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(package / "package.json", destination / "package.json")
    shutil.copy2(package / "LICENSE", destination / "LICENSE")
    for name in ("dist", "public"):
        if (destination / name).exists():
            shutil.rmtree(destination / name)
        if (package / name).is_dir():
            shutil.copytree(package / name, destination / name)
    wasm_env = dict(env, KITU_OSC_IR_WASM_CRATE=str(source / "crates" / "kitu-osc-ir-wasm"),
                    KITU_ADMIN_WASM_OUT_DIR=str(root / "admin" / "static" / "kitu-osc-ir-wasm"))
    command([args.pnpm, "--dir", package, "run", "wasm"], root, wasm_env)
    lock = root / "admin" / "pnpm-lock.yaml"
    before = lock.read_text(encoding="utf-8")
    command([args.pnpm, "--dir", root / "admin", "install", "--no-frozen-lockfile" if override else "--frozen-lockfile"], root, env)
    lock_diff = save_diff(root, "admin/pnpm-lock.yaml", before) if override else None
    if not override and lock.read_text(encoding="utf-8") != before:
        raise SetupError("pinned Admin setup unexpectedly changed pnpm-lock.yaml")
    command([args.pnpm, "--dir", root / "admin", "run", "check"], root, env)
    command([args.pnpm, "--dir", root / "admin", "run", "build"], root, env)
    return lock_diff


def setup(args, root=ROOT):
    root = root.resolve(strict=True)
    env = os.environ.copy()
    cargo_home = Path(env.get("CARGO_HOME", str(root / ".kitu" / "cargo"))).expanduser().resolve()
    cargo_home.mkdir(parents=True, exist_ok=True)
    env["CARGO_HOME"] = str(cargo_home)
    target = check_versions(args, root, env)
    dependencies, url, pinned = pinned_dependencies(root)
    if not (root / "Cargo.lock").is_file():
        raise SetupError("checked-in Cargo.lock is missing; setup requires the repository lockfile")
    original_lock = (root / "Cargo.lock").read_bytes()
    original_manifest = (root / "Cargo.toml").read_bytes()
    effective = root
    requested = None
    if args.kitu_path:
        requested = args.kitu_path.expanduser().resolve(strict=True)
        source_revision(requested, env, require_clean=False)
        members = kitu_members(requested, dependencies)
        effective = copy_working_demo(root, env)
        override_manifest(effective, members)
        resolve(effective, args.cargo, env, target, locked=False)
        lock_diff = save_diff(effective, "Cargo.lock", original_lock.decode("utf-8"))
    else:
        lock_diff = None
    metadata = resolve(effective, args.cargo, env, target)
    source, packages = resolved_source(effective, metadata, requested)
    revision, status = source_revision(source, env, require_clean=not args.kitu_path)
    if not args.kitu_path and (revision != pinned or any(not (p.get("source") or "").endswith("#" + pinned) for p in packages)):
        raise SetupError("resolved Kitu revision differs from the committed full revision")
    # This helper rejects mixed origins and records actual package roots, graph,
    # lock/config guards; build.rs later rereads every source byte.
    command([sys.executable, effective / "tools" / "prepare-kitu-build.py", "--manifest-path", effective / "app" / "Cargo.toml",
             "--cargo", args.cargo, "--target", target], effective, env)
    inputs = json.loads((effective / "app" / "kitu-build-inputs.json").read_text(encoding="utf-8"))
    pnpm_diff = None if args.rust_only else build_admin(effective, source, args, env, bool(args.kitu_path))
    final_revision, final_status = source_revision(source, env, require_clean=not args.kitu_path)
    if final_revision != revision:
        raise SetupError("Kitu HEAD changed during setup; rerun against a stable source checkout")
    if (root / "Cargo.toml").read_bytes() != original_manifest:
        raise SetupError("original Cargo.toml changed during setup")
    if (root / "Cargo.lock").read_bytes() != original_lock:
        raise SetupError("original Cargo.lock changed during setup")
    selection = {"schema": 1, "path": str(source), "revision": revision, "mode": "override" if args.kitu_path else "pinned",
                 "effectiveDemoRoot": str(effective), "originalDemoRoot": str(root), "cargoHome": str(cargo_home),
                 "repository": url, "pinnedRevision": pinned, "target": target, "rustOnly": args.rust_only,
                 "sourceStatus": final_status, "cargoLockSha256": sha(effective / "Cargo.lock"),
                 "graphSha256": hashlib.sha256(json.dumps(inputs["graph"], sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                 "kituPackages": [{"name": p["name"], "manifestPath": p["manifest_path"], "source": p.get("source")} for p in sorted(packages, key=lambda p: p["name"])],
                 "overrideLockDiff": lock_diff, "overridePnpmLockDiff": pnpm_diff}
    selection["dependencyInputs"] = dependency_inputs(effective,
        [package["manifest_path"] for package in metadata["packages"]
         if package["id"] in metadata["workspace_members"]], cargo_home)
    validate_graph_selection(effective, selection, inputs)
    write_json(effective / ".kitu" / "source.json", selection)
    write_json(root / ".kitu" / "source.json", selection)
    print(f"Prepared {selection['mode']} demo: {effective}\nKitu {revision}: {source}")
    return selection


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kitu-path", type=Path, help="use this Kitu Git checkout in a new isolated demo copy")
    parser.add_argument("--rust-only", action="store_true", help="prepare Rust dependencies and identity without Node/Admin")
    parser.add_argument("--cargo", default=os.environ.get("CARGO", "cargo"))
    parser.add_argument("--rustc", default=os.environ.get("RUSTC", "rustc"))
    parser.add_argument("--node", default="node")
    parser.add_argument("--pnpm", default="pnpm")
    args = parser.parse_args(argv)
    try:
        setup(args)
        return 0
    except (OSError, ValueError, KeyError, StopIteration, SetupError, subprocess.CalledProcessError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
