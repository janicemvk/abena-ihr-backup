#!/bin/bash
# Fix sc-network enum indices in Cargo git cache. Run from project root.
# Re-run after cargo update (or when SDK checkout changes).

for MSG in $(find /root/.cargo/git/checkouts -path "*/substrate/client/network/src/protocol/message.rs" 2>/dev/null); do
  echo "Fixing: $MSG"
  # First remove any bad #[codec(index = N)] we may have added (7-15 only; keep 6 and 17)
  sed -i.bak '/^[[:space:]]*#\[codec(index = 7)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 8)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 9)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 10)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 11)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 12)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 13)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 14)\][[:space:]]*$/d' "$MSG"
  sed -i.bak '/^[[:space:]]*#\[codec(index = 15)\][[:space:]]*$/d' "$MSG"
  rm -f "${MSG}.bak"

  # Restore from git if file is in a git repo (removes all our edits)
  (cd "$(dirname "$MSG")/../../../../.." 2>/dev/null && git checkout -- substrate/client/network/src/protocol/message.rs 2>/dev/null) || true
done

# Now add ONLY before enum variants - use pattern that matches comment+variant (not struct)
# The enum has "RemoteCallRequest(RemoteCallRequest)," - same phrase in both; struct has "pub struct"
# We match: line with /// comment, AND next line has "VariantName(" and ")," (enum variant)
for MSG in $(find /root/.cargo/git/checkouts -path "*/substrate/client/network/src/protocol/message.rs" 2>/dev/null); do
  # Use perl for multi-line: only insert when comment is followed by enum variant line
  perl -i -0pe '
    s/(    \/\/\/ Remote method call request\.\n)(    RemoteCallRequest\([^)]+\)\),)/$1    #[codec(index = 7)]\n$2/;
    s/(    \/\/\/ Remote method call response\.\n)(    RemoteCallResponse\([^)]+\)\),)/$1    #[codec(index = 8)]\n$2/;
    s/(    \/\/\/ Remote storage read request\.\n)(    RemoteReadRequest\([^)]+\)\),)/$1    #[codec(index = 9)]\n$2/;
    s/(    \/\/\/ Remote storage read response\.\n)(    RemoteReadResponse\([^)]+\)\),)/$1    #[codec(index = 10)]\n$2/;
    s/(    \/\/\/ Remote header request\.\n)(    RemoteHeaderRequest\([^)]+\)\),)/$1    #[codec(index = 11)]\n$2/;
    s/(    \/\/\/ Remote header response\.\n)(    RemoteHeaderResponse\([^)]+\)\),)/$1    #[codec(index = 12)]\n$2/;
    s/(    \/\/\/ Remote changes request\.\n)(    RemoteChangesRequest\([^)]+\)\),)/$1    #[codec(index = 13)]\n$2/;
    s/(    \/\/\/ Remote changes response\.\n)(    RemoteChangesResponse\([^)]+\)\),)/$1    #[codec(index = 14)]\n$2/;
    s/(    \/\/\/ Remote child storage read request\.\n)(    RemoteReadChildRequest\([^)]+\)\),)/$1    #[codec(index = 15)]\n$2/;
  ' "$MSG"
done

echo "Done. Run: cargo build --release -p abena-node"
