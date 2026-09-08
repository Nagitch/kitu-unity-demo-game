#!/usr/bin/env python3
"""Run the standalone demo Compose stack using its Cargo Kitu pin."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.yml"
KITU_REPOSITORY = "https://github.com/Nagitch/kitu-logic-processor"
REVISION_PATTERN = re.compile(r"[0-9a-f]{40}")


class ComposeContractError(RuntimeError):
    pass


def _document(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ComposeContractError(f"missing {path}") from exc


def _repository(url: str) -> str:
    return url.removesuffix(".git")


def pinned_kitu() -> tuple[str, str, tuple[str, ...]]:
    """Return the one Kitu Git source declared by the workspace manifest."""
    dependencies = _document(ROOT / "Cargo.toml").get("workspace", {}).get("dependencies", {})
    selected = {name: value for name, value in dependencies.items() if name.startswith("kitu-")}
    if not selected:
        raise ComposeContractError("Cargo.toml declares no workspace Kitu dependencies")

    pins: set[tuple[str, str]] = set()
    for name, value in selected.items():
        if not isinstance(value, dict) or "git" not in value or "rev" not in value:
            raise ComposeContractError(f"{name} must declare a Git URL and full rev")
        if any(key in value for key in ("path", "branch", "tag")):
            raise ComposeContractError(f"{name} must not use path, branch, or tag")
        revision = value["rev"]
        if not isinstance(revision, str) or not REVISION_PATTERN.fullmatch(revision):
            raise ComposeContractError(f"{name} rev must be one lowercase 40-character SHA")
        repository = _repository(value["git"])
        pins.add((repository, revision))

    if len(pins) != 1:
        raise ComposeContractError("all workspace Kitu dependencies must share one Git URL and revision")
    repository, revision = pins.pop()
    if repository != KITU_REPOSITORY:
        raise ComposeContractError(f"unsupported Kitu repository {repository!r}; expected {KITU_REPOSITORY!r}")
    return repository, revision, tuple(sorted(selected))


def contract() -> dict:
    repository, revision, dependencies = pinned_kitu()
    return {
        "repository": repository,
        "revision": revision,
        "dependencies": list(dependencies),
    }


def run_compose(command: str, extra: list[str], profiles: list[str], compose_file: Path | None = None) -> int:
    compose_file = (compose_file or COMPOSE_FILE).resolve()
    if not compose_file.is_file():
        raise ComposeContractError(f"missing {compose_file}")
    repository, revision, _ = pinned_kitu()
    environment = os.environ.copy()
    # These values are consumed by both Dockerfiles. They are derived from
    # Cargo.toml on every invocation, so a gateway cannot drift from the app.
    environment.update(KITU_REPOSITORY=repository, KITU_REV=revision)
    environment["PUBLIC_KITU_ADMIN_WT_URL"] = (
        "https://localhost:9443" if "webtransport" in profiles else ""
    )
    argv = ["docker", "compose", "-f", str(compose_file)]
    for profile in profiles:
        argv.extend(("--profile", profile))
    argv.append(command)
    argv.extend(extra)
    return subprocess.run(argv, cwd=ROOT, env=environment, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, help="explicit Compose file (defaults to this demo docker-compose.yml)")
    parser.add_argument("--profile", action="append", default=[], help="enable an optional Compose profile")
    parser.add_argument("command", choices=("config", "up", "down", "build", "ps", "logs", "run", "cp", "contract"))
    parser.add_argument("args", nargs=argparse.REMAINDER, help="arguments passed to docker compose")
    args = parser.parse_args(argv)
    try:
        if args.command == "contract":
            if args.args:
                parser.error("contract does not accept extra arguments")
            print(json.dumps(contract(), indent=2))
            return 0
        return run_compose(args.command, args.args, args.profile, args.file)
    except ComposeContractError as exc:
        print(f"compose contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
