set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

setup:
    python3 tools/setup.py

setup-local kitu_path:
    python3 tools/setup.py --kitu-path "{{kitu_path}}"

verify scope="all" evidence=".tmp/verification":
    python3 tools/run.py python3 tools/verify-repository.py --scope "{{scope}}" --evidence "{{evidence}}"

native evidence=".tmp/native":
    python3 tools/run.py python3 tools/verify-arena-macos.py --scope native --evidence "{{evidence}}"

full evidence=".tmp/full":
    python3 tools/run.py python3 tools/verify-arena-macos.py --scope full --evidence "{{evidence}}"

host:
    python3 tools/run.py cargo run --locked -p kitu-demo-game --bin kitu-demo-game-admin-host

admin:
    python3 tools/run.py pnpm --dir admin dev
