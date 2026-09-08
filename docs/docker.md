# Docker Compose

The root Compose file runs the extracted demo as a clean, standalone checkout.
The application host listens on `http://localhost:8787` and the Admin dev
server on `http://localhost:5173`. The optional WebTransport gateway listens on
UDP `9443`.

`tools/compose.py` reads every `kitu-*` entry in the root `Cargo.toml`. It
requires one Kitu repository and one full 40-character revision, then passes
that exact pair to every Docker build. The Compose file intentionally has no
revision fallback: use the wrapper so an app and gateway build cannot drift.
This keeps the gateway implementation in the fetched Kitu checkout. The
command does not read or write `.kitu/source.json`, prepared maps, or host
lock-diff files.

Check the resolved contract and Compose model without building images:

```sh
python3 tools/compose.py contract
python3 tools/compose.py config
```

Start the HTTP host and Admin:

```sh
python3 tools/compose.py up --build
```

Include the optional gateway by placing its profile before the Compose command:

```sh
python3 tools/compose.py --profile webtransport up --build
```

The image contains the pinned application content under `app/content`. The
first container start seeds that content into the persistent `arena-content`
volume. Named volumes also retain `app/.arena/runs` and
`app/.arena/recordings`; source files and the host's `.kitu` directory are
never mounted into the containers. The Admin container runs `tools/setup.py`
in its own filesystem before starting pnpm, so its prepared Kitu identity is
container-local.

To import a Tanu-edited content file explicitly, copy it into the content
volume after the stack is up:

```sh
python3 tools/compose.py cp ./app/content/arena.tmd demo-game:/workspace/app/content/arena.tmd
```

The always-on `cert-init` service owns certificate creation and renewal. It
uses the existing Kitu contract: an ECDSA `prime256v1` key, a 13-day localhost
certificate, and the SHA-256 digest of the DER certificate. Admin, gateway and
smoke services wait for that service to complete and source the shared
`webtransport.env`; the digest is also retained in `webtransport-cert.sha256`.
The gateway itself remains disabled unless the `webtransport` profile is
enabled.

Run the selected Kitu gateway smoke client through Compose so its working
directory and source are explicit:

```sh
python3 tools/compose.py --profile webtransport run --rm gateway-smoke
```

Local coordinated framework overrides continue to use
`tools/setup.py --kitu-path` and `tools/run.py`; Docker uses the committed
Cargo pin.
