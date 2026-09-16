# Repository role

This repository owns the Unity demo application: Rust game rules/hosts/native
factory, Unity project, app-specific Admin routes/content and scenarios.
Reusable Kitu implementation belongs to kitu-logic-processor and is consumed
through its public interfaces. Do not copy framework implementation here.

Keep Unity .meta/GUIDs, ABI symbols, protocol IDs and immutable baseline/expected
fixture bytes unchanged unless the task explicitly requires such a change.
Historical evidence must not be rewritten as current validation.

Use tools/setup.py for pinned dependencies or its explicit --kitu-path override;
use tools/run.py when executing the selected dependency configuration. Do not
mix Rust, common Admin and WASM from different Kitu revisions. Lockfile changes
require explicit dependency updates or an isolated override checkout.

Run repository-local checks appropriate to the change. Python verification
reports require an absent evidence directory. Native/full verification runs on
macOS, and full requires licensed Unity 6000.6.0f1. Preserve unrelated generated
Unity settings after verification. Never claim an unexecuted gate passed.

## Arena message contract

Before adding or changing an Arena OSC message, read
`docs/specs/arena-events.md`. Keep its catalog, JSON Schemas, authored semantics
and examples in `docs/contracts/arena-v1/` consistent with the implementation.
Regenerate the reference with `python3 tools/arena_contracts.py generate`; do not
hand-edit its generated region. Run the `contracts` verification scope (with
`tools/requirements-contracts.txt` installed), plus behavior tests for changes to
emission conditions, order, duplication, pause or replay. New addresses and
payload variants need examples and real trace coverage. Review compatibility
before changing the wire shape or meaning; do not silently rewrite v1 fixtures.
