"""Insert unique #[codec(index = 7..15)] on Message enum variants (patches/sc-network)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MSG = ROOT / "patches" / "sc-network" / "src" / "protocol" / "message.rs"

OLD = (
    "\t\t/// Remote method call request.\n"
    "\t\tRemoteCallRequest(RemoteCallRequest<Hash>),\n"
    "\t\t/// Remote method call response.\n"
    "\t\tRemoteCallResponse(RemoteCallResponse),\n"
    "\t\t/// Remote storage read request.\n"
    "\t\tRemoteReadRequest(RemoteReadRequest<Hash>),\n"
    "\t\t/// Remote storage read response.\n"
    "\t\tRemoteReadResponse(RemoteReadResponse),\n"
    "\t\t/// Remote header request.\n"
    "\t\tRemoteHeaderRequest(RemoteHeaderRequest<Number>),\n"
    "\t\t/// Remote header response.\n"
    "\t\tRemoteHeaderResponse(RemoteHeaderResponse<Header>),\n"
    "\t\t/// Remote changes request.\n"
    "\t\tRemoteChangesRequest(RemoteChangesRequest<Hash>),\n"
    "\t\t/// Remote changes response.\n"
    "\t\tRemoteChangesResponse(RemoteChangesResponse<Number, Hash>),\n"
    "\t\t/// Remote child storage read request.\n"
    "\t\tRemoteReadChildRequest(RemoteReadChildRequest<Hash>),"
)

NEW = (
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
    "\t\tRemoteReadChildRequest(RemoteReadChildRequest<Hash>),"
)

# polkadot-stable2407 style (no type params on enum variants)
OLD_2407 = (
    "\t\t/// Remote method call request.\n"
    "\t\tRemoteCallRequest(RemoteCallRequest),\n"
    "\t\t/// Remote method call response.\n"
    "\t\tRemoteCallResponse(RemoteCallResponse),\n"
    "\t\t/// Remote storage read request.\n"
    "\t\tRemoteReadRequest(RemoteReadRequest),\n"
    "\t\t/// Remote storage read response.\n"
    "\t\tRemoteReadResponse(RemoteReadResponse),\n"
    "\t\t/// Remote header request.\n"
    "\t\tRemoteHeaderRequest(RemoteHeaderRequest),\n"
    "\t\t/// Remote header response.\n"
    "\t\tRemoteHeaderResponse(RemoteHeaderResponse),\n"
    "\t\t/// Remote changes request.\n"
    "\t\tRemoteChangesRequest(RemoteChangesRequest),\n"
    "\t\t/// Remote changes response.\n"
    "\t\tRemoteChangesResponse(RemoteChangesResponse),\n"
    "\t\t/// Remote child storage read request.\n"
    "\t\tRemoteReadChildRequest(RemoteReadChildRequest),"
)

NEW_2407 = (
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
    "\t\tRemoteReadChildRequest(RemoteReadChildRequest),"
)


def main() -> None:
    if not MSG.is_file():
        raise SystemExit(f"Missing {MSG}")
    t = MSG.read_text(encoding="utf-8")
    if NEW in t or NEW_2407 in t:
        print("Already patched (generic or 2407 layout)")
        return
    if OLD in t:
        MSG.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
        print(f"Patched {MSG} (generic enum)")
        return
    if OLD_2407 in t:
        MSG.write_text(t.replace(OLD_2407, NEW_2407, 1), encoding="utf-8")
        print(f"Patched {MSG} (2407-style enum)")
        return
    raise SystemExit(
        "Could not find expected enum block. Re-download message.rs from polkadot-sdk "
        "or fix patches/sc-network/src/protocol/message.rs manually."
    )


if __name__ == "__main__":
    main()
