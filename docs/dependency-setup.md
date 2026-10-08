# Dependency setup

Use Python 3.11 or newer, Rust/Cargo 1.96.0, Node.js 24 and pnpm 11.9.0. The Rust toolchain is declared in `rust-toolchain.toml`. No Kitu crate or Admin package publication is required.

```sh
python3 tools/setup.py
python3 tools/run.py cargo test --locked -p kitu-demo-game
python3 tools/run.py pnpm --dir admin dev
```

Setup requires the checked-in `Cargo.lock` and `admin/pnpm-lock.yaml`. Every workspace Kitu Git dependency must name the same full 40-character revision. Cargo fetches that revision, and setup selects its actual resolved Git checkout for the Rust dependencies, shared Admin package and WASM build. The checkout must have no local changes; Cargo's own untracked `.cargo-ok` completion marker is excluded from that check.

The default Cargo cache is `.kitu/cargo`. An explicitly configured `CARGO_HOME` is honored and saved in the selection. `run.py` restores that Cargo home and the selected Kitu/WASM paths. Both `run.py COMMAND ...` and `run.py -- COMMAND ...` pass arguments directly without a shell.

Default setup validates `admin/kitu-package/package.json` against the shared Admin manifest in the selected Kitu checkout, installs the shared Admin package with its frozen lockfile, checks/tests/builds it, copies its public package artifacts into `admin/kitu-package`, builds WASM, then installs/checks/builds the demo Admin with its frozen lockfile. The application consumes the shared package through `file:./kitu-package`. Setup rejects a missing or different manifest before running Admin builds; it does not silently replace the committed dependency contract.

Only the shared package's manifest is checked in. It is an exact JSON copy from `tools/kitu-web-admin/package/package.json` at the Kitu revision in `Cargo.toml`, making its dependencies and peer dependencies available to pnpm and Dependabot before setup. The package's implementation, `dist`, `public`, and `LICENSE` artifacts are not vendored; setup still obtains them from the same Kitu source as Rust and WASM. The generated directories and license are ignored. Old `.kitu/admin-package` caches are no longer consumed.

When updating the Kitu revision, refresh this manifest from that revision if it changed, then refresh `admin/pnpm-lock.yaml` and run setup. Dependabot may update the application's registry dependencies, but this manifest stays tied to the Kitu pin. Dependency-only operations do not need Rust, WASM, or package build outputs:

```sh
pnpm --dir admin install --lockfile-only --ignore-scripts --no-frozen-lockfile
git diff --exit-code -- admin/package.json admin/pnpm-lock.yaml admin/kitu-package/package.json
```

The frontend CI runs this check before setup to catch regressions in clean-checkout dependency resolution. A successful dependency-only install is not a usable Admin build; run setup before checking, building, or serving the application.

For a Rust-only environment:

```sh
python3 tools/setup.py --rust-only
python3 tools/run.py cargo test --locked -p kitu-demo-game
```

## Local Kitu development

```sh
python3 tools/setup.py --kitu-path ../kitu-logic-processor
python3 tools/run.py cargo test --locked -p kitu-demo-game
```

Each invocation creates a new independent Git checkout under `.kitu/overrides/demo-*`. It preserves the demo's original HEAD/index and copies its current tracked and eligible untracked files, including working changes and deletions. Generated caches, existing overrides, Cargo targets, Node dependencies and Unity generated directories are excluded.

Only the copy's workspace Kitu dependencies become paths to the requested Kitu checkout. All reachable app and native Kitu packages must resolve to that source. The copy receives an effective Cargo lockfile and, for Admin setup, the local Kitu Admin manifest and an updated pnpm lockfile. The original demo's dependency manifests and lockfiles remain unchanged. Existing override checkouts are retained.

`.kitu/source.json` records the selected Kitu path, HEAD revision, mode, effective demo root, Cargo cache, package origins, graph digest and lockfile digest. An override also records its Cargo/pnpm lock diff paths. The original demo selection points to the effective copy, so subsequent `tools/run.py` commands operate there. Selection is published only after setup succeeds.

Portable and native verification reports retain sanitized dependency identities in their evidence directory's `source/`: the Kitu revision and mode, package names, hashes of local source changes, resolved graph hashes, effective Cargo/pnpm lock hashes, and available override lock diff hashes. Absolute checkout paths, raw source selection, lock contents and diff contents remain local. The report's `dependencySource` links are relative to the evidence directory. Graph identities are captured initially and after explicit preparation for each portable compiler scope or native Cargo invocation. A null lock diff means setup did not produce one, such as the pnpm diff in Rust-only setup. A failed partial setup does not publish a successful selection.

Running setup without `--kitu-path` selects the original demo and its pinned dependency again. The previous copies remain available for inspection. If the selected Kitu HEAD changes, rerun setup. Rust source edits at the same Kitu HEAD in override mode are reread by the build identity. Changes to demo dependency manifests, lockfiles or Cargo configuration require rerunning setup; `run.py` rejects the stale selection before starting a command. Prepared dependency graphs must also resolve Kitu to the selected root and Git/path origin. The demo copy captures the demo files at setup time: rerun setup after editing the original demo, and after changing shared Admin or WASM code, to refresh the selected application and package artifacts.

## Setup checks

```sh
python3 -m unittest tools/tests/test_setup.py
KITU_SETUP_CARGO_INTEGRATION=1 python3 -m unittest tools/tests/test_setup_cargo.py
```

The integration test creates tiny local Git repositories with no registry dependencies. It exercises a pinned Cargo checkout, a dirty local Kitu override, the independent effective Git identity, command routing, lockfile preservation and reset to the pinned selection.
