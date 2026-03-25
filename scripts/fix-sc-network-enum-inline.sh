#!/bin/bash
# Replace Message enum tail (after Consensus through before "Batch of consensus") with correct indices.
# Run from repo root: bash scripts/fix-sc-network-enum-inline.sh

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MSG="$ROOT/patches/sc-network/src/protocol/message.rs"

if [[ ! -f "$MSG" ]]; then
  echo "Missing $MSG"
  exit 1
fi

python3 - "$MSG" << 'PY'
import re
import sys
from pathlib import Path

msg = Path(sys.argv[1])
t = msg.read_text(encoding="utf-8")

# After Consensus line, before "/// Batch of consensus protocol messages."
anchor_start = r"(\t\tConsensus\(ConsensusMessage\),\n)"
anchor_end = r"(\t\t/// Batch of consensus protocol messages\.)"

# Try tab-indented (upstream Substrate)
block_generic = (
    "\t\t/// Remote method call request.\n"
    "\t\t#[codec(index = 7)]\n"
    "\t\tRemoteCallRequest(RemoteCallRequest<Hash>),\n"
    "\t\t/// Remote method call response.\n"
    "\t\t#[codec(index = 8)]\n"
    "\t\tRemoteCallResponse(RemoteCallResponse),\n"
    "\t\t/// Remote storage read request.\n"
    "\t\t#[codec(index = 9)]\n"
    "\t\tRemoteReadRequest(RemoteReadRequest<Hash>),\n"
    "\t\t/// Remote storage read response.\n"
    "\t\t#[codec(index = 10)]\n"
    "\t\tRemoteReadResponse(RemoteReadResponse),\n"
    "\t\t/// Remote header request.\n"
    "\t\t#[codec(index = 11)]\n"
    "\t\tRemoteHeaderRequest(RemoteHeaderRequest<Number>),\n"
    "\t\t/// Remote header response.\n"
    "\t\t#[codec(index = 12)]\n"
    "\t\tRemoteHeaderResponse(RemoteHeaderResponse<Header>),\n"
    "\t\t/// Remote changes request.\n"
    "\t\t#[codec(index = 13)]\n"
    "\t\tRemoteChangesRequest(RemoteChangesRequest<Hash>),\n"
    "\t\t/// Remote changes response.\n"
    "\t\t#[codec(index = 14)]\n"
    "\t\tRemoteChangesResponse(RemoteChangesResponse<Number, Hash>),\n"
    "\t\t/// Remote child storage read request.\n"
    "\t\t#[codec(index = 15)]\n"
    "\t\tRemoteReadChildRequest(RemoteReadChildRequest<Hash>),\n"
)

block_2407 = (
    "\t\t/// Remote method call request.\n"
    "\t\t#[codec(index = 7)]\n"
    "\t\tRemoteCallRequest(RemoteCallRequest),\n"
    "\t\t/// Remote method call response.\n"
    "\t\t#[codec(index = 8)]\n"
    "\t\tRemoteCallResponse(RemoteCallResponse),\n"
    "\t\t/// Remote storage read request.\n"
    "\t\t#[codec(index = 9)]\n"
    "\t\tRemoteReadRequest(RemoteReadRequest),\n"
    "\t\t/// Remote storage read response.\n"
    "\t\t#[codec(index = 10)]\n"
    "\t\tRemoteReadResponse(RemoteReadResponse),\n"
    "\t\t/// Remote header request.\n"
    "\t\t#[codec(index = 11)]\n"
    "\t\tRemoteHeaderRequest(RemoteHeaderRequest),\n"
    "\t\t/// Remote header response.\n"
    "\t\t#[codec(index = 12)]\n"
    "\t\tRemoteHeaderResponse(RemoteHeaderResponse),\n"
    "\t\t/// Remote changes request.\n"
    "\t\t#[codec(index = 13)]\n"
    "\t\tRemoteChangesRequest(RemoteChangesRequest),\n"
    "\t\t/// Remote changes response.\n"
    "\t\t#[codec(index = 14)]\n"
    "\t\tRemoteChangesResponse(RemoteChangesResponse),\n"
    "\t\t/// Remote child storage read request.\n"
    "\t\t#[codec(index = 15)]\n"
    "\t\tRemoteReadChildRequest(RemoteReadChildRequest),\n"
)


def try_fix(start_pat: str, end_pat: str, block: str, text: str):
    pat = start_pat + r"(.*?)" + end_pat
    m = re.search(pat, text, flags=re.DOTALL)
    if not m:
        return None
    return text[: m.end(1)] + block + text[m.start(3) :]


pairs = [
    (anchor_start, anchor_end),
    (
        anchor_start.replace("\t\t", "        "),
        anchor_end.replace("\t\t", "        "),
    ),
]

for start, end in pairs:
    for block in (block_generic, block_2407):
        b = block.replace("\t\t", "        ") if start.startswith("        ") else block
        n = try_fix(start, end, b, t)
        if n is not None:
            msg.write_text(n, encoding="utf-8")
            print(f"Patched {msg}")
            sys.exit(0)

print("Pattern not found (Consensus / Batch anchors).", file=sys.stderr)
sys.exit(1)
PY

echo "Done. Run: cargo build --release -p abena-node"
