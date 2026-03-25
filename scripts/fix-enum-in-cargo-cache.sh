#!/bin/bash
# Patch sc-network message.rs in Cargo's git cache (for when [patch] doesn't apply)
# Run from project root. Re-run after cargo update.

MSG_FILE=$(find /root/.cargo/git/checkouts -path "*/substrate/client/network/src/protocol/message.rs" 2>/dev/null | head -1)

if [ -z "$MSG_FILE" ] || [ ! -f "$MSG_FILE" ]; then
  echo "Error: message.rs not found. Run 'cargo build' once to fetch deps."
  exit 1
fi

echo "Patching: $MSG_FILE"

# Insert #[codec(index = N)] before each variant (Consensus has 6; next need 7-15)
# Using sed: /pattern/ inserts before the line; we need to add the attribute line
sed -i.bak \
  -e '/^[[:space:]]*\/\/\/ Remote method call request\.$/a\    #[codec(index = 7)]' \
  -e '/^[[:space:]]*\/\/\/ Remote method call response\.$/a\    #[codec(index = 8)]' \
  -e '/^[[:space:]]*\/\/\/ Remote storage read request\.$/a\    #[codec(index = 9)]' \
  -e '/^[[:space:]]*\/\/\/ Remote storage read response\.$/a\    #[codec(index = 10)]' \
  -e '/^[[:space:]]*\/\/\/ Remote header request\.$/a\    #[codec(index = 11)]' \
  -e '/^[[:space:]]*\/\/\/ Remote header response\.$/a\    #[codec(index = 12)]' \
  -e '/^[[:space:]]*\/\/\/ Remote changes request\.$/a\    #[codec(index = 13)]' \
  -e '/^[[:space:]]*\/\/\/ Remote changes response\.$/a\    #[codec(index = 14)]' \
  -e '/^[[:space:]]*\/\/\/ Remote child storage read request\.$/a\    #[codec(index = 15)]' \
  "$MSG_FILE"

rm -f "${MSG_FILE}.bak" 2>/dev/null
echo "Done. Run: cargo build --release -p abena-node"
