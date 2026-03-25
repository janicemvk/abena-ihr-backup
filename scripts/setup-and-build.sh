#!/bin/bash
# One-shot: populate patches/sc-network, align lockfile, build abena-node.
# Run from workspace root:  bash scripts/setup-and-build.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
bash ./scripts/setup-sc-network-patch.sh
cargo build --release -p abena-node
