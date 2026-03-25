#!/bin/bash
# Rust 1.88+ errors on #[no_mangle] + #[panic_handler] in sp-io (polkadot-stable2407).
# Run after `cargo fetch` or a failed build, then rebuild.

set -e
for f in $(find "${HOME}/.cargo/git/checkouts" -path "*/substrate/primitives/io/src/lib.rs" 2>/dev/null); do
  if grep -q '#\[panic_handler\]' "$f" && grep -A1 '#\[panic_handler\]' "$f" | grep -q '#\[no_mangle\]'; then
    echo "Patching: $f"
    perl -i -0pe 's/#\[panic_handler\]\r?\n#\[no_mangle\]\r?\n/#\[panic_handler\]\n/s' "$f"
  fi
done
echo "Done. Run: cargo build --release -p abena-node"
