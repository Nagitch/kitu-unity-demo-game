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
