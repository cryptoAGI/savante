#!/usr/bin/env python3
"""bind/savante_publish.py — turn the verified bundle into mint parameters. Offline. Signs nothing.

    python3 bind/savante_publish.py                       # identity + rung + the mint parameters
    python3 bind/savante_publish.py --calldata            # + the exact mintOpenAgent calldata
    python3 bind/savante_publish.py --manifest-only       # the canonical manifest bytes, for diffing
    python3 bind/savante_publish.py --ar-id <tx>          # storageURI = ar://<tx>, once an upload exists
    python3 bind/savante_publish.py --upload-command      # print the permanence command; never runs it

What this program will NOT do, by construction:

  * create a wallet or touch a vault  — the pre-existing factory did this even on a dry run, so a
    "dry" run left an EVM identity and a vault entry behind. Nothing here writes outside stdout.
  * make a network call                — no RPC, no gateway, no upload. It prints what to send.
  * invent a content root              — the root is keccak256 over the canonical manifest bytes and
    is reproducible from the repository alone. No salt, no timestamp. (The factory derived its root
    from os.urandom, which cannot be checked by anyone, including its author.)
  * claim a rung it has not earned     — `referenced` until an upload receipt exists.
  * fabricate a sealed key             — the mint parameters target mintOpenAgent, whose sealedKeyHash
    is zero because this office seals nothing.

Exit codes: 0 the manifest reproduced and the parameters are printed; 2 the manifest is stale or
inconsistent (fix by re-running the binder); 1 anything else.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import savante_bind as sb  # noqa: E402

# iNFT2 mintOpenAgent — no sealedKeyHash parameter; that is the whole point of the function.
MINT_OPEN_SIG = "mintOpenAgent(address,bytes32,string,bytes32,uint256,uint8,string)"

DEFAULT_DIMENSIONS = 768        # on the iNFT_7857 whitelist (_isValidDimension)
DEFAULT_PARALLEL_UNITS = 1

EXIT_OK, EXIT_ERR, EXIT_STALE = 0, 1, 2


# ── minimal ABI encoding (the same hand-rolled approach savante_verify uses) ───

def _word(n: int) -> bytes:
    return n.to_bytes(32, "big")


def _pad(b: bytes) -> bytes:
    return b + b"\x00" * ((32 - len(b) % 32) % 32)


def _enc_string(s: str) -> bytes:
    raw = s.encode("utf-8")
    return _word(len(raw)) + _pad(raw)


def encode_mint_open(to: str, content_root: str, storage_uri: str, metadata_root: str,
                     dimensions: int, parallel_units: int, token_uri: str) -> str:
    """0x || selector || head(7 words) || tail. Dynamic args are storageURI (2) and tokenURI (6)."""
    selector = sb.keccak256(MINT_OPEN_SIG.encode("utf-8"))[:4]
    addr = bytes.fromhex(to[2:].rjust(40, "0"))
    head_words = 7
    tail_a = _enc_string(storage_uri)
    off_a = head_words * 32
    off_b = off_a + len(tail_a)
    head = (
        _word(int.from_bytes(addr, "big"))
        + bytes.fromhex(content_root[2:])
        + _word(off_a)
        + bytes.fromhex(metadata_root[2:])
        + _word(dimensions)
        + _word(parallel_units)
        + _word(off_b)
    )
    return "0x" + (selector + head + tail_a + _enc_string(token_uri)).hex()


# ── the bundle, re-verified before anything is printed ────────────────────────

def load_and_verify(repo: Path) -> Tuple[Dict[str, Any], Dict[str, Any], bytes]:
    """Read the manifest and the ledger, and prove the manifest still describes the files on disk.

    Printing mint parameters derived from a stale manifest would be the whole failure mode of this
    program, so it refuses rather than warns."""
    mpath, lpath = repo / sb.MANIFEST_NAME, repo / sb.LEDGER_NAME
    for p in (mpath, lpath):
        if not p.is_file():
            print(f"error: {p} does not exist — run `python3 bind/savante_bind.py` first", file=sys.stderr)
            raise SystemExit(EXIT_STALE)

    raw = mpath.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    ledger = json.loads(lpath.read_text(encoding="utf-8"))

    problems: List[str] = []

    # 1. every facet still hashes to what the manifest says.
    for f in manifest.get("facets", []):
        fp = repo / f["path"]
        if not fp.is_file():
            problems.append(f"facet `{f['facet']}`: {f['path']} is missing")
            continue
        data = fp.read_bytes()
        if sb.sha256_hex(data) != f["sha256"] or len(data) != f["bytes"]:
            problems.append(f"facet `{f['facet']}` ({f['path']}) has changed since the last bind")

    # 2. the manifest's own identity reproduces from its canonical form.
    canon = sb.canonical_bytes({k: v for k, v in manifest.items() if k != "identity"})
    ident = manifest.get("identity") or {}
    if ident.get("thot") != "thot:" + sb.sha256_hex(canon):
        problems.append("manifest identity does not reproduce from its canonical bytes")
    if ident.get("contentRoot") != "0x" + sb.keccak256(canon).hex():
        problems.append("manifest contentRoot does not reproduce from its canonical bytes")

    # 3. the ledger points at this manifest.
    lb = ledger.get("bundle") or {}
    if (lb.get("file") or {}).get("sha256") not in (None, sb.sha256_hex(raw)):
        problems.append("the ledger's bundle.file.sha256 is not this manifest file")

    if problems:
        print("STALE — the bundle does not describe the working tree:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("\nRe-run `python3 bind/savante_bind.py`, then `python3 bind/savante_verify.py .`", file=sys.stderr)
        raise SystemExit(EXIT_STALE)

    return manifest, ledger, raw


def mint_parameters(manifest: Dict[str, Any], ledger: Dict[str, Any], raw: bytes,
                    ar_id: Optional[str], token_uri: Optional[str]) -> Dict[str, Any]:
    """Every value here is derived from bytes in the repository. Nothing is generated."""
    ident = manifest["identity"]
    file_sha = sb.sha256_hex(raw)

    if ar_id:
        storage_uri = f"ar://{ar_id}"
        storage_note = "an Arweave transaction id supplied by the operator"
    else:
        storage_uri = f"local://{file_sha}"
        storage_note = ("nothing is uploaded, so the URI is the local content address. An ipfs:// or "
                        "ar:// URI here would name a location that does not hold these bytes.")

    card_digest = ((ledger.get("card") or {}).get("digest") or {}).get("keccak256_canonical")

    return {
        "function": MINT_OPEN_SIG,
        "why_open": ("this office seals nothing, so sealedKeyHash is absent rather than fabricated; "
                     "mintAgent would revert on a zero hash and a non-zero one would claim a key that "
                     "does not exist"),
        "to": None,   # the operator's custody address; this program does not choose it
        "contentRoot": ident["contentRoot"],
        "contentRoot_source": "keccak256(canonical manifest bytes) — reproducible from the repo alone",
        "storageURI": storage_uri,
        "storageURI_note": storage_note,
        "metadataRoot": card_digest,
        "metadataRoot_source": "the agent card's canonical keccak256, from the ledger",
        "dimensions": DEFAULT_DIMENSIONS,
        "parallelUnits": DEFAULT_PARALLEL_UNITS,
        "tokenURI": token_uri or "",
        "tokenURI_note": ("empty unless the operator supplies one: the card is not pinned anywhere, and "
                          "an unpinned ipfs:// URI is a promise nothing keeps"),
        "thot": ident["thot"],
        "cid": ident["cid"],
        "name": ident["name"],
        "rung": (manifest.get("rung") or {}).get("value"),
        "manifest_file_sha256": file_sha,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Derive iNFT2 mintOpenAgent parameters from the verified facet bundle. Offline; signs nothing.")
    ap.add_argument("repo", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--manifest-only", action="store_true", help="print the canonical manifest bytes and exit")
    ap.add_argument("--calldata", action="store_true", help="also print the ABI-encoded call")
    ap.add_argument("--to", default="0x0000000000000000000000000000000000000000",
                    help="custody address for the calldata preview (default: the zero address, which the contract rejects)")
    ap.add_argument("--ar-id", help="an Arweave transaction id, once one exists; sets storageURI to ar://<id>")
    ap.add_argument("--token-uri", help="tokenURI, if the operator has pinned the card somewhere")
    ap.add_argument("--upload-command", action="store_true", help="print the permanence command; this program never runs it")
    a = ap.parse_args(argv)

    repo = a.repo.resolve()
    sb.keccak_selftest()
    manifest, ledger, raw = load_and_verify(repo)

    if a.manifest_only:
        sys.stdout.write(sb.canonical_bytes({k: v for k, v in manifest.items() if k != "identity"}).decode("utf-8"))
        sys.stdout.write("\n")
        return EXIT_OK

    p = mint_parameters(manifest, ledger, raw, a.ar_id, a.token_uri)

    print("BUNDLE")
    print(f"  facets        {len(manifest['facets'])} present, {len(manifest.get('absent', []))} absent with reasons")
    print(f"  thot          {p['thot']}")
    print(f"  cid           {p['cid']}")
    print(f"  name          {p['name']}")
    print(f"  rung          {p['rung']}  (evidence: no commit tx, no data tx, no attestation)")
    print()
    print("MINT PARAMETERS — iNFT2." + MINT_OPEN_SIG.split("(")[0])
    print(f"  contentRoot   {p['contentRoot']}")
    print(f"  storageURI    {p['storageURI']}")
    print(f"  metadataRoot  {p['metadataRoot']}")
    print(f"  dimensions    {p['dimensions']}")
    print(f"  parallelUnits {p['parallelUnits']}")
    print(f"  tokenURI      {p['tokenURI']!r}")
    print(f"  to            <operator's custody address — not chosen by this program>")

    if a.calldata:
        print()
        print("CALLDATA (preview; `to` is --to, default the zero address the contract rejects)")
        print("  " + encode_mint_open(a.to, p["contentRoot"], p["storageURI"], p["metadataRoot"],
                                      p["dimensions"], p["parallelUnits"], p["tokenURI"]))

    if a.upload_command:
        print()
        print("UPLOAD — the operator runs this; this program does not")
        print(f"  node ~/permanence/dapp.mjs put {repo / sb.MANIFEST_NAME} \\")
        print("       --jwk <key.json> --rung stored --tag kind=sagi.thot_manifest \\")
        print(f"       --tag thot={p['thot']} --no-encrypt")
        print("  Then re-run with --ar-id <returned tx id>, and record the receipt in the ledger.")

    print()
    print("Nothing was signed, uploaded, or written. A mint is the operator's signature.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
