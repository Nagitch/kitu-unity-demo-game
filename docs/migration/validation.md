# Extraction and split validation

This record describes repository-split validation on 2026-09-08. The earlier
checkout and CI snapshot used these candidate revisions:

| Repository role | Revision | Review |
| --- | --- | --- |
| Reusable Admin and external-application boundary | Kitu `337620708c41929dfc8a365c2dc12591d506d44b` | [Kitu PR 170](https://github.com/Nagitch/kitu-logic-processor/pull/170) |
| Framework-only Kitu tree | Kitu `ed72415f7d92070a06739a253e2a6ed73fa09e9e` | [Kitu PR 171](https://github.com/Nagitch/kitu-logic-processor/pull/171) |
| Standalone application | Demo `dff7baac444c00b2fa132ab4819ec8e3d16deede` | [demo PR 1](https://github.com/Nagitch/kitu-unity-demo-game/pull/1) |
| Coordinated pins | Workspace `d191d848537b0d9b4d89163ee2ad573b88e8e0cd` | [workspace PR 44](https://github.com/Nagitch/kitu-workspace/pull/44) |

All four pull requests remain unmerged. The results below validate these
candidate revisions; they do not claim that the migration has been integrated
into the default branches.

## Extraction and retained-history checks

- Compared all 599 files at the extraction boundary with their original Git
  blobs. Unity metadata, immutable oracle fixtures and historical evidence were
  also compared after the application overlay; their bytes remain unchanged.
- Verified all 1,018 historical blobs in the filtered history were available
  from an anonymous clone of the public source repository. The sole tracked LFS
  object was retrieved anonymously and its SHA-256 matched.
- Reference verification passed for the 28-tick preparation trace and the
  5,528-tick stock death/retry trace.
- Before the final framework removal, the extracted Rust workspace executed 181
  tests across 24 suites with no failures or ignored cases. Formatting, Clippy,
  documentation and data/tool verification passed. The shared Admin package and
  its starter also passed package-consumer, lifecycle, Svelte and production
  base-path checks.
- Both retained old recordings were rejected specifically for incompatible
  execution identity. The 697-file legacy archive was copied and verified
  byte-for-byte; neither the old recordings nor matching executables changed.

The source-identity relocation checks confirmed that equivalent source trees
produce the same identity after relocation, a same-commit Rust source edit
changes the identity, and stale prepared Cargo manifest/lock inputs are
rejected. Setup now binds dependency manifests, locks and Cargo configuration;
the command runner rejects stale bindings, and evidence capture checks that
resolved Kitu roots and package origins match the active selection.

## Standalone and coordinated checkout checks

- A fresh remote checkout of demo `e4708adf6fac6a46d5251c4cde4ab5b5a31fe902`
  hydrated the tracked LFS asset, selected the pinned Kitu
  `337620708c41929dfc8a365c2dc12591d506d44b`, completed normal setup, passed
  reference verification and the Admin lint/check/19-test gates, generated the
  selected-source WASM, left manifests and lockfiles unchanged, and finished
  clean.
- The same fresh demo was prepared through `--kitu-path` against framework
  `ed72415f7d92070a06739a253e2a6ed73fa09e9e`. Its frontend and data scopes
  passed, every resolved Kitu package came from the requested source, the
  effective override recorded its Cargo lock adaptation, and the original demo
  manifests, locks and working tree stayed unchanged.
- A final fresh clone of workspace `d191d848537b0d9b4d89163ee2ad573b88e8e0cd`
  initialized framework `ed72415f7d92070a06739a253e2a6ed73fa09e9e` and demo
  `dff7baac444c00b2fa132ab4819ec8e3d16deede`. Normal setup, WASM, all 10 shared
  Admin package tests, its Svelte and production builds, the contract check for
  all 12 Kitu dependency pins, reference verification and LFS hydration passed. The Cargo and Admin
  locks were unchanged, all three repositories were clean, and unrelated
  submodules remained uninitialized.
- CI passed all six jobs for the framework-only candidate, all four external
  demo compatibility jobs, all eight demo jobs and both workspace jobs at the
  revisions listed above.

## Runtime checks

- A production browser run using demo `1c4defe0f2e4e7d84a8aa563bd49d63afe01bb91`
  with framework `ed72415f7d92070a06739a253e2a6ed73fa09e9e` opened the root
  WebSocket, loaded the Arena Inspector from the configured HTTP endpoint and
  showed `obj-1` after the existing World HTTP spawn operation. There were no
  browser console errors.
- A separate explicit browser import initialized the public WASM module; its
  JavaScript and `.wasm` requests both returned HTTP 200 and it generated a
  typed `/admin/world/spawn` message. That message was deliberately not sent,
  so this proves the public loader contract rather than claiming that the World
  operation used WASM.
- The full macOS attempt at demo
  `dff7baac444c00b2fa132ab4819ec8e3d16deede` passed preflight, source-package,
  native test/build, C ABI, default Unity Player build and owned server/replay
  provisioning. It then failed during Unity EditMode because a test still used
  the former in-tree fixture path; all later full-scope steps were recorded as
  `notRun`, and cleanup restored generated settings and stopped the owned server.
- The selected-source fixture resolver added after that failure passed all 64
  focused codec EditMode cases, including 51 golden fixtures, with no failures
  or skips. It also passed a manual Editor launch with no inherited
  `KITU_SOURCE_PATH`; both runs left no unexpected project changes. These focused
  results do not turn the interrupted full attempt into a full pass.

## Final full verification

The new `full` attempt at clean demo
`61d675a3267e673c2cc0ff6197e681a79d5423fe`, consuming Kitu
`ed72415f7d92070a06739a253e2a6ed73fa09e9e`, passed all 18 required steps.
The same demo commit passed all eight CI jobs. The compact
[full verification record](full-verification.json) preserves the source
identities, counts and digest of the retained complete report.

Unity executed 143 EditMode, 31 MessagePack PlayMode and 7 JSON PlayMode cases,
with zero failures or skips. Rust read back all 11 valid C# fixture pairs.
Inspection identities matched across native and network execution. With the
owned external server stopped, the default Player completed all four required
scenarios (9,186 ticks), and the edited-package Player completed its separate
1,800-tick scenario with the same native library. Relocation, no-overwrite,
invalid-content rejection and edited-content startup probes all passed.
Cleanup stopped owned processes, restored generated project settings, and
reported no unexpected tracked changes.

## Additional environment and visual checks

The full run's screenshots exposed overlapping HUD text outside the world
camera's viewport. All 41 inspected rendering sources, scenes, project settings
and pipeline assets were byte-identical to the pre-extraction source, including
the exact Stage 18 build source. The Kitu client did not clear its HUD bands;
the Unity-only `ArenaHud` already did. A separate application change applies that
same camera-relative clear before the Kitu HUD draws, preserving GUI color and
leaving the frozen comparison implementation unchanged. The full record above
predates this drawing-only follow-up; its focused Player validation is separate.
The historical trigger is unproven, so this does not claim that earlier captures
had the same visual defect.

The additional final Docker application check remains unexecuted. An earlier isolated
Docker build at `6b6f71b7afd67e176058091b3493716ca97eb3d8` passed health and
WebTransport datagram smoke checks, but the final rebuild could not run because
OrbStack was stopped and Docker Desktop's filesystem was read-only. A decision
to start OrbStack or hold that extra gate is still pending; the earlier result
is not a pass for the final image.
The final pinned Compose configuration, including the WebTransport profile,
passed `python3 tools/compose.py --profile webtransport config --quiet` without
starting a daemon or containers.

Merge and promotion remain separate review actions for the four pull
requests listed above. Historical Stage 18 evidence under `docs/verification/`
retains its original source identities and is not evidence for a new run of the
split candidates.
