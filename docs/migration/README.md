# Repository extraction

The source and filtered commits, unchanged extracted-file count and path mapping
are recorded in `source-map.json`. The complete `git filter-repo` commit map is
retained in `commit-map.tsv`. Filtering ran in a dedicated clone; the original
Kitu history and tags were not rewritten. The original MIT license remains at
the repository root.

The in-game Arena name, crate/binary names, ABI symbols and network identifiers
are unchanged. The new name allows a future Unreal demo to sit alongside this
Unity demo without changing game behavior.

`tests/scenarios/arena/reference/baseline.json` is an immutable record of the
original Unity-only comparison source. Its original `sourceSha256` paths are
resolved through the path map. The baseline revision and expected values are
not replaced by filtered commit IDs. Likewise, `docs/verification/` retains
historical source identities, paths and results.

New source layout and dependency identities yield new replay execution IDs.
Old recordings must remain paired with their original executables and native
libraries in the existing runtime archives. No archive or old recording is
rewritten, and no replay-compatibility check is relaxed.

Migration validation is recorded in [validation.md](validation.md). Pending
checks are not included as passed evidence.

To validate a saved recording against the current executable, run:

```sh
python3 tools/run.py cargo run --locked -p kitu-demo-game --example replay-compatibility -- /path/to/saved.tsq
```

For the migration rejection check, append `--expect-incompatible`. This mode
succeeds only when the recording is rejected specifically for its execution
identity; a malformed/truncated recording is still a failure. It prints the
recording hash, current execution identity and diagnostic without editing the
recording.
