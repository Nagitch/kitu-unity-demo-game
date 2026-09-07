FROM rust:1.96.0-bookworm

ARG KITU_REPOSITORY
ARG KITU_REV
ENV KITU_REPOSITORY_PIN=${KITU_REPOSITORY} \
    KITU_REV_PIN=${KITU_REV}

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
        git \
        git-lfs \
        libssl-dev \
        openssl \
        pkg-config \
        python3 \
        python3-venv \
    && curl --fail --silent --show-error --location https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install --yes --no-install-recommends nodejs \
    && corepack enable \
    && corepack prepare pnpm@11.9.0 --activate \
    && rustup target add wasm32-unknown-unknown \
    && git lfs install --system \
    && rm -rf /var/lib/apt/lists/*

ENV CARGO_REGISTRIES_CRATES_IO_PROTOCOL=sparse \
    CARGO_TARGET_DIR=/workspace/target \
    RUSTUP_TOOLCHAIN=1.96.0

WORKDIR /workspace
COPY . .

LABEL org.nagitch.kitu.repository="${KITU_REPOSITORY}" \
      org.nagitch.kitu.revision="${KITU_REV}"

RUN test -n "${KITU_REPOSITORY}" \
    && test -n "${KITU_REV}" \
    && python3 -c 'import os, tomllib; d=tomllib.load(open("Cargo.toml", "rb"))["workspace"]["dependencies"]; p=[v for n,v in d.items() if n.startswith("kitu-")]; r={v.get("rev") for v in p}; g={v.get("git", "").removesuffix(".git") for v in p}; assert r == {os.environ["KITU_REV_PIN"]} and g == {os.environ["KITU_REPOSITORY_PIN"].removesuffix(".git")}, "Docker Kitu build args do not match Cargo.toml"'

# setup.py resolves the Kitu source from Cargo.toml and creates container-local
# identity under .kitu. No host source.json, lock diff, or prepared map is used.
RUN python3 tools/setup.py --rust-only \
    && cargo build --locked -p kitu-demo-game --bin kitu-demo-game-admin-host

EXPOSE 8787
CMD ["cargo", "run", "--locked", "-p", "kitu-demo-game", "--bin", "kitu-demo-game-admin-host"]
