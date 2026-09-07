# Extraction validation

The extraction preserves the original Kitu history and records its path and
commit mapping alongside this document. The application adaptation consumes
Kitu `337620708c41929dfc8a365c2dc12591d506d44b` through the locked source-selection
workflow. Later framework removal and workspace integration are separate steps.

## Completed checks

- Compared all 599 files at the extraction boundary with their original Git
  blobs. Unity metadata, immutable oracle fixtures and historical evidence were
  also compared after the application overlay; their bytes remain unchanged.
- Verified all 1,018 historical blobs in the filtered history were already
  available from an anonymous clone of the public source repository. The sole
  tracked LFS object was retrieved anonymously and its SHA-256 matched.
- Reference verification passed for the 28-tick preparation trace and the
  5,528-tick stock death/retry trace.
- The extracted Rust workspace executed 181 tests across 24 suites with no
  failures or ignored cases. Formatting, Clippy, documentation and data/tool
  verification passed.
- The application Admin passed lint, Svelte check, all 19 inspection tests and
  its production build, including WASM from the selected Kitu revision.
- Native verification at the revision above passed all 28 declared native
  tests, the native doctest, native build, and C ABI trace comparisons. An
  initial verification failure exposed an old rustdoc path in the case
  manifest; the path was corrected and its parser regression test added before
  the successful rerun.
- Both retained old recordings were rejected specifically for incompatible
  execution identity. The 697-file legacy archive was copied and verified
  byte-for-byte; neither the old recordings nor matching executables changed.
- Independent consumers of the shared Admin package passed production browser
  checks at `/` and `/review`, including navigation, WebSocket connection and
  successful WASM JavaScript/binary requests.

The source-identity relocation check also confirmed that equivalent source trees
produce the same identity after relocation, a same-commit Rust source edit changes
the identity, and stale prepared Cargo manifest/lock inputs are rejected.
An additional real Cargo/Git regression reproduced a stale setup after repinning
the demo. Setup now binds dependency manifests, locks and Cargo configuration;
the command runner rejects stale bindings, and evidence capture checks that
resolved Kitu roots and package origins match the active selection.

## Remaining migration gates

Fresh remote checkout, the final framework-only checkout, the external-demo CI
against that framework revision, final workspace pins, and licensed Unity/Player
acceptance must be recorded separately. A native or portable pass does not imply
that the full Unity scope ran.

An earlier isolated Docker build at `6b6f71b7afd67e176058091b3493716ca97eb3d8`
passed health and WebTransport datagram smoke checks. The later rebuild was
interrupted by host storage exhaustion and a read-only Docker filesystem. That
earlier result is not a pass for the final image or full Docker application flow.
