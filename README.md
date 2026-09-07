# Kitu Unity Demo Game

A compact, playable Endless Arena game demonstrating Kitu's authoritative Rust
runtime through Unity, a standalone server, an embedded native runtime and a
Svelte Admin application. The game and protocol still use the existing Arena
names; the repository name identifies the engine integration.

## Contents

- `app/`: Rust game rules, server host, native C ABI library and authored content.
- `unity/`: Unity 6000.6.0f1 project, including the Unity-only comparison baseline.
- `admin/`: the SvelteKit application and Arena-specific screens.
- `tests/scenarios/`: application scenarios and immutable comparison fixtures.
- `tools/`: dependency setup, packaging, build and verification commands.
- `docs/`: application contracts, development guidance and historical evidence.

Reusable Kitu crates, the common `@kitu/admin` package and its minimal starter,
the CLI and the WebTransport gateway belong to
[Kitu](https://github.com/Nagitch/kitu-logic-processor). This repository consumes
those interfaces and does not vendor their production implementation.

## Setup

Use Rust **1.96.0**, Python **3.11 or later**, Node **24**, pnpm **11.9.0** and Git
LFS. macOS native builds require the Apple SDK; Unity/Player verification also
requires a licensed Unity **6000.6.0f1** installation.

```sh
git clone https://github.com/Nagitch/kitu-unity-demo-game.git
cd kitu-unity-demo-game
git lfs pull
python3 tools/setup.py
python3 tools/run.py cargo run --locked -p kitu-demo-game --bin kitu-demo-game-admin-host
```

In another terminal, run `python3 tools/run.py pnpm --dir admin dev` and open
`http://localhost:5173`. The default host endpoint is `http://localhost:8787`.
Open the actual Unity project with `cd unity` followed by `unity open .`.

The complete Kitu revision in `Cargo.toml` is the source for Rust, shared Admin,
WASM and native builds. Setup downloads that source into ignored `.kitu/`
cache directories. No sibling checkout or package registry publication is
required. Package and Cargo lockfiles define the normal reproducible build.

For coordinated work, run `python3 tools/setup.py --kitu-path /absolute/path/to/kitu-logic-processor`.
The explicit override prepares a separate demo copy, records its effective
lock changes and makes `tools/run.py` execute in that copy. It substitutes Rust,
Admin and WASM together. Run setup without the override to return to the pinned
source. Do not run bare Cargo commands in the original checkout expecting the
temporary override to apply.

## Verification

```sh
python3 tools/run.py python3 tools/verify-repository.py --scope all --evidence .tmp/portable-1
python3 tools/run.py python3 tools/verify-arena-macos.py --scope native --evidence .tmp/native-1
python3 tools/run.py python3 tools/verify-arena-macos.py --scope full --evidence .tmp/full-1
```

Each evidence directory must be new. The full scope launches licensed Unity and
real Players; a portable or native-only pass does not replace that check.
[Build verification](docs/specs/arena-build-verification.md) details the cases.

## History and recordings

The application history was extracted from Kitu without rewriting the original
repository. `docs/migration/source-map.json` records old and new paths;
`docs/migration/commit-map.tsv` records commit translation. Unity `.meta` files
and GUIDs, the baseline metadata, recorded oracle values and historical evidence
are preserved. Historical evidence describes its original source revision, not
a new successful run in this repository.

Replay compatibility includes the actual compiled source and dependency graph.
Use the original matching executable for old recordings. Migration does not
convert those recordings or weaken compatibility checks. See
[the migration record](docs/migration/README.md).
