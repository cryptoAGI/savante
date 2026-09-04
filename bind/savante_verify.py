#!/usr/bin/env python3
"""bind/savante_verify.py — the third-party checker. One grep gates both a merge and a purchase.

    python3 bind/savante_verify.py [REPO]                       # steps 1-5, offline, no trust in the author
    python3 bind/savante_verify.py REPO --onchain --rpc URL --registry ADDR --agent-id N   # + step 6

Steps (spec §8):
  1. sha256 + cid_v1_raw over the raw bytes of savante.persona; compare to savante.commitments.json.
  2. Preflight P1/P2; resolve the fifteen doctrine pointers in order; recompute the doctrine root; compare.
  3. Recompute sha256 + CID for .claude/agents/savante.md and .claude/skills/sagi/SKILL.md; compare.
  4. Parse the charter YAML frontmatter `tools:` line; the allowlist must be EXACTLY Read, Grep, Glob, Bash.
     Any Edit, Write or Agent is a hard REJECT. The same list must equal /token/intelligence/tool_allowlist.
  5. md5(repo persona) == md5(mindX mirror persona). Absent mirror → a condition, not a rejection
     (a holder on another machine has no mindX); present-and-different → REJECT.
  6. --onchain: eth_call getMetadata(agentId,"savanteDoctrineRoot") and compare to the local root; eth_getLogs
     for MetadataSet(agentId, keccak(key)) and read the FIRST value; a change between first and current is a
     FINDING, not an error. ABI encoded by hand over raw JSON-RPC (urllib); eth_abi cross-checks when importable.
     Signatures from the ERC-8004 draft text: getMetadata(uint256,string) returns (bytes) — erc-8004.md:131;
     event MetadataSet(uint256 indexed agentId, string indexed indexedMetadataKey, string metadataKey,
     bytes metadataValue) — erc-8004.md:138. All three flags are required; there is no default RPC or address.

Also recomputes the card CID / sha256 / canonical digest against the ledger.

Emits FINDINGS / VERDICT / RATIONALE / CONDITIONS / RISKS WATCHED and exits 0 ONLY on `VERDICT: APPROVE`
(1 = APPROVE_WITH_CONDITIONS, 2 = REJECT, 3 = DEFER).

Shares its primitives with savante_bind.py by import so the two cannot drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import savante_bind as sb  # noqa: E402

EXPECTED_TOOLS = ["Read", "Grep", "Glob", "Bash"]
FORBIDDEN_TOOLS = {"Edit", "Write", "Agent"}
EXIT = {"APPROVE": 0, "APPROVE_WITH_CONDITIONS": 1, "REJECT": 2, "DEFER": 3}


class Report:
    def __init__(self) -> None:
        self.findings: List[str] = []
        self.rejects: List[str] = []
        self.conditions: List[str] = []
        self.risks: List[str] = []

    def ok(self, msg: str) -> None:
        self.findings.append("KNOWN   " + msg)

    def unknown(self, msg: str, condition: str) -> None:
        self.findings.append("NOT_YET_KNOWN  " + msg)
        self.conditions.append(condition)

    def reject(self, msg: str) -> None:
        self.findings.append("FAIL    " + msg)
        self.rejects.append(msg)

    def note(self, msg: str) -> None:
        self.findings.append("FINDING " + msg)


# ── steps 1-5 ─────────────────────────────────────────────────────────────────

def check_artifact(rep: Report, repo: Path, ledger: Dict[str, Any], name: str) -> Optional[bytes]:
    entry = (ledger.get("artifacts") or {}).get(name)
    if not isinstance(entry, dict):
        rep.reject(f"ledger has no artifacts.{name}")
        return None
    path = repo / entry.get("path", "")
    if not path.is_file():
        rep.reject(f"{entry.get('path')} missing from the repository")
        return None
    data = path.read_bytes()
    sha = sb.sha256_hex(data)
    cid, _ = sb.cid_or_none(data)
    if sha != entry.get("sha256"):
        rep.reject(f"{entry['path']}: sha256 {sha} != ledger {entry.get('sha256')}")
    elif cid != entry.get("cid"):
        rep.reject(f"{entry['path']}: cid {cid} != ledger {entry.get('cid')}")
    elif len(data) != entry.get("bytes"):
        rep.reject(f"{entry['path']}: {len(data)} bytes != ledger {entry.get('bytes')}")
    else:
        rep.ok(f"{entry['path']}: {len(data)} B, sha256 {sha}, cid {cid} — match the ledger")
    return data


def check_doctrine_root(rep: Report, persona: Any, ledger: Dict[str, Any]) -> Optional[str]:
    pre = sb.preflight(persona)
    if not pre["ok"]:
        for e in pre["errors"]:
            rep.reject(f"preflight {e['rule']} at {e['pointer']}: {e['reason']}")
        return None
    rep.ok(f"preflight P1+P2 pass: {pre['property_name_count']} property names, all ASCII; "
           f"numbers {[n['value'] for n in pre['numbers']]}")
    dr = ledger.get("doctrine_root") or {}
    if dr.get("pointers") != sb.DOCTRINE_POINTERS:
        rep.reject(f"ledger doctrine pointers differ from the fixed fifteen: {dr.get('pointers')}")
        return None
    clauses = []
    preimage = b""
    for p in sb.DOCTRINE_POINTERS:
        try:
            v = sb.resolve(persona, p)
        except sb.PointerMissing as e:
            rep.reject(f"doctrine pointer missing: {e}")
            return None
        cb = sb.canonical_bytes(v)
        preimage += p.encode("utf-8") + b"\x1f" + cb + b"\x1e"
        clauses.append((p, sb.sha256_hex(cb)))
    root = "0x" + sb.keccak256(preimage).hex()
    if root != dr.get("value"):
        rep.reject(f"doctrine root {root} != ledger {dr.get('value')}")
        ledger_clauses = {c.get("pointer"): c.get("canonical_sha256") for c in dr.get("clauses", []) if isinstance(c, dict)}
        for p, h in clauses:
            if ledger_clauses.get(p) != h:
                rep.note(f"clause changed: {p}")
        return root
    rep.ok(f"doctrine root {root} over {len(clauses)} pointers ({len(preimage)} B preimage) — matches the ledger")
    return root


def parse_frontmatter_tools(charter: bytes) -> Optional[List[str]]:
    text = charter.decode("utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^tools:\s*(.*)$", line)
        if m:
            return [t.strip() for t in m.group(1).split(",") if t.strip()]
    return None


def check_tools(rep: Report, charter: Optional[bytes], persona: Any) -> None:
    if charter is None:
        return
    tools = parse_frontmatter_tools(charter)
    if tools is None:
        rep.reject("charter frontmatter has no `tools:` line — the allowlist is not declared")
        return
    forbidden = sorted(FORBIDDEN_TOOLS & set(tools))
    if forbidden:
        rep.reject(f"charter allowlist grants {forbidden}: oversight that can act is oversight no longer")
    elif tools != EXPECTED_TOOLS:
        rep.reject(f"charter allowlist {tools} is not exactly {EXPECTED_TOOLS}")
    else:
        rep.ok(f"charter frontmatter tools: {', '.join(tools)} — exactly the read-only allowlist")
    try:
        declared = sb.resolve(persona, "/token/intelligence/tool_allowlist")
    except sb.PointerMissing:
        declared = None
    if declared != tools:
        rep.reject(f"persona /token/intelligence/tool_allowlist {declared} != charter frontmatter {tools}")
    else:
        rep.ok("persona tool_allowlist equals the charter frontmatter")


def check_mirror(rep: Report, persona_bytes: Optional[bytes], mirror: Path, skip: bool) -> None:
    if persona_bytes is None:
        return
    if skip:
        rep.unknown(f"mirror check skipped (--no-mirror-check): {mirror} not compared",
                    f"run without --no-mirror-check on the host holding {mirror}")
        return
    if not mirror.is_file():
        rep.unknown(f"mirror {mirror} not present on this host; step 5 cannot be decided here",
                    f"on the author's host, assert md5 {sb.md5_hex(persona_bytes)} == md5({mirror})")
        return
    a, b = sb.md5_hex(persona_bytes), sb.md5_hex(mirror.read_bytes())
    if a != b:
        rep.reject(f"mirror drift: md5 repo {a} != mirror {b} ({mirror}) — the ledger commits to one document "
                   f"while corpus.PERSONA_DIR teaches another")
    else:
        rep.ok(f"mirror md5 {a} equal at {mirror}")


def check_card(rep: Report, repo: Path, ledger: Dict[str, Any], root: Optional[str], persona_sha: Optional[str]) -> None:
    c = ledger.get("card") or {}
    path = repo / c.get("path", sb.CARD_NAME)
    if not path.is_file():
        rep.reject(f"{c.get('path', sb.CARD_NAME)} missing")
        return
    data = path.read_bytes()
    cur = c.get("current")
    ver = (c.get("versions") or {}).get(cur) or {}
    cid, _ = sb.cid_or_none(data)
    if cid != ver.get("cid") or sb.sha256_hex(data) != ver.get("sha256"):
        rep.reject(f"card {cur}: cid {cid} / sha256 {sb.sha256_hex(data)} != ledger {ver.get('cid')} / {ver.get('sha256')}")
        return
    try:
        card = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        rep.reject(f"card is not valid JSON: {e}")
        return
    pre = sb.preflight(card)
    if not pre["ok"]:
        rep.reject(f"card fails preflight: {pre['errors']}")
        return
    digest = "0x" + sb.keccak256(sb.canonical_bytes(card)).hex()
    if digest != (c.get("digest") or {}).get("keccak256_canonical"):
        rep.reject(f"card digest {digest} != ledger {(c.get('digest') or {}).get('keccak256_canonical')}")
        return
    rep.ok(f"card {cur}: cid {cid}, canonical keccak {digest} — match the ledger")
    if card.get("type") != sb.ERC8004_TYPE:
        rep.reject(f"card.type is {card.get('type')!r}, not the ERC-8004 registration-v1 literal")
    integ = (card.get("savante") or {}).get("integrity") or {}
    if root and integ.get("doctrine_root") != root:
        rep.reject(f"card.savante.integrity.doctrine_root {integ.get('doctrine_root')} != recomputed {root}")
    if persona_sha and integ.get("persona_sha256") != persona_sha:
        rep.reject(f"card.savante.integrity.persona_sha256 != recomputed {persona_sha}")
    regs = card.get("registrations")
    erc = ((ledger.get("bindings") or {}).get("erc8004") or {})
    if regs == [] and ledger.get("mint") is None and erc.get("agentId") is None:
        rep.ok("card.registrations is empty and the ledger records no mint — consistent: nothing is minted")
    elif regs != [] and ledger.get("mint") is None:
        rep.reject(f"card.registrations {regs} asserts a registration the ledger does not record")
    slots = ledger.get("onchain_slots") or {}
    if persona_sha and (slots.get("savantePersonaDigest") or {}).get("value") != "0x" + persona_sha:
        rep.reject("ledger onchain_slots.savantePersonaDigest.value != recomputed persona sha256")
    if root and (slots.get("savanteDoctrineRoot") or {}).get("value") != root:
        rep.reject("ledger onchain_slots.savanteDoctrineRoot.value != recomputed doctrine root")


# ── step 6: raw JSON-RPC, hand-rolled ABI ─────────────────────────────────────

def abi_word(n: int) -> bytes:
    return n.to_bytes(32, "big")


def abi_pad(b: bytes) -> bytes:
    return b + b"\x00" * (-len(b) % 32)


def encode_get_metadata(agent_id: int, key: str) -> bytes:
    """getMetadata(uint256,string): head = [uint256, offset 0x40]; tail = [len, padded utf-8]."""
    selector = sb.keccak256(b"getMetadata(uint256,string)")[:4]
    kb = key.encode("utf-8")
    encoded = abi_word(agent_id) + abi_word(0x40) + abi_word(len(kb)) + abi_pad(kb)
    try:
        import eth_abi  # type: ignore
        ref = eth_abi.encode(["uint256", "string"], [agent_id, key])
        if bytes(ref) != encoded:
            raise RuntimeError("hand-rolled ABI encoding disagrees with eth_abi")
    except ImportError:
        pass
    return selector + encoded


def decode_dynamic(data: bytes, offset: int) -> bytes:
    if offset + 32 > len(data):
        raise ValueError("dynamic offset beyond data")
    ln = int.from_bytes(data[offset:offset + 32], "big")
    start = offset + 32
    if start + ln > len(data):
        raise ValueError("dynamic length beyond data")
    return data[start:start + ln]


def decode_bytes_return(data: bytes) -> bytes:
    if len(data) < 64:
        raise ValueError(f"return data too short ({len(data)} B) for `bytes`")
    off = int.from_bytes(data[:32], "big")
    return decode_dynamic(data, off)


def decode_metadataset_data(data: bytes) -> Tuple[str, bytes]:
    """Non-indexed part of MetadataSet: (string metadataKey, bytes metadataValue)."""
    if len(data) < 64:
        raise ValueError("log data too short")
    off_key = int.from_bytes(data[:32], "big")
    off_val = int.from_bytes(data[32:64], "big")
    return decode_dynamic(data, off_key).decode("utf-8", errors="replace"), decode_dynamic(data, off_val)


class Rpc:
    def __init__(self, url: str) -> None:
        self.url = url
        self.n = 0

    def call(self, method: str, params: List[Any]) -> Any:
        self.n += 1
        body = json.dumps({"jsonrpc": "2.0", "id": self.n, "method": method, "params": params}).encode()
        req = urllib.request.Request(self.url, data=body, headers={"content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read().decode("utf-8"))
        if "error" in resp:
            raise RuntimeError(f"{method}: {resp['error']}")
        return resp.get("result")


def hexb(s: str) -> bytes:
    return bytes.fromhex(s[2:] if s.startswith("0x") else s)


def check_onchain(rep: Report, ledger: Dict[str, Any], root: Optional[str], persona_sha: Optional[str],
                  rpc_url: str, registry: str, agent_id: int) -> None:
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", registry):
        rep.reject(f"--registry {registry!r} is not a 20-byte hex address")
        return
    rpc = Rpc(rpc_url)
    try:
        chain_id = int(rpc.call("eth_chainId", []), 16)
        rep.note(f"rpc {rpc_url} reports eth_chainId {chain_id}; registry {registry}; agentId {agent_id} "
                 f"(all three supplied by the caller — nothing here comes from the ledger)")
    except Exception as e:
        rep.reject(f"rpc unreachable or invalid: {e}")
        return
    erc = ((ledger.get("bindings") or {}).get("erc8004") or {})
    bound = erc.get("agentRegistry")
    if isinstance(bound, str):
        if bound.lower() != f"eip155:{chain_id}:{registry}".lower():
            rep.reject(f"ledger bindings.erc8004.agentRegistry {bound} != eip155:{chain_id}:{registry}")
    else:
        rep.note("ledger records no agentRegistry binding (nothing minted); the on-chain read below is "
                 "informational — it can show what the chain holds, not that the ledger claims it")

    for key, local in (("savanteDoctrineRoot", root), ("savantePersonaDigest", "0x" + persona_sha if persona_sha else None)):
        try:
            data = encode_get_metadata(agent_id, key)
            ret = rpc.call("eth_call", [{"to": registry, "data": "0x" + data.hex()}, "latest"])
            current = decode_bytes_return(hexb(ret)) if ret else b""
        except Exception as e:
            rep.reject(f"getMetadata({agent_id},{key!r}) failed: {e}")
            continue
        cur_hex = "0x" + current.hex() if current else None
        if not current:
            rep.reject(f"getMetadata({agent_id},{key!r}) is empty — the slot is not written; nothing is bound")
        elif local is None:
            rep.note(f"{key} on chain = {cur_hex}; local value unavailable (earlier step failed)")
        elif cur_hex.lower() == local.lower():
            rep.ok(f"{key} on chain {cur_hex} == local")
        else:
            rep.reject(f"{key} on chain {cur_hex} != local {local}")

        # History: FIRST MetadataSet for this key.
        topic0 = "0x" + sb.keccak256(b"MetadataSet(uint256,string,string,bytes)").hex()
        topics = [topic0, "0x" + abi_word(agent_id).hex(), "0x" + sb.keccak256(key.encode()).hex()]
        try:
            logs = rpc.call("eth_getLogs", [{"address": registry, "fromBlock": "0x0", "toBlock": "latest", "topics": topics}])
        except Exception as e:
            rep.unknown(f"MetadataSet history for {key!r} unavailable from this RPC: {e}",
                        f"read the FIRST MetadataSet({agent_id}, keccak({key!r})) event from an archive RPC and compare it to {cur_hex}")
            continue
        if not logs:
            rep.note(f"no MetadataSet event for {key!r} found from block 0 — either never set or the RPC prunes logs")
            continue
        logs.sort(key=lambda lg: (int(lg.get("blockNumber", "0x0"), 16), int(lg.get("logIndex", "0x0"), 16)))
        try:
            k0, v0 = decode_metadataset_data(hexb(logs[0]["data"]))
        except Exception as e:
            rep.note(f"first MetadataSet log for {key!r} undecodable: {e}")
            continue
        first_hex = "0x" + v0.hex()
        where = f"block {int(logs[0]['blockNumber'], 16)} tx {logs[0].get('transactionHash')}"
        if k0 != key:
            rep.note(f"first MetadataSet decoded key {k0!r} != {key!r} (indexed topic matched by hash)")
        if cur_hex and first_hex.lower() != cur_hex.lower():
            rep.note(f"{key} was RE-SET: first value {first_hex} ({where}) != current {cur_hex}; {len(logs)} MetadataSet events. "
                     f"Compare against the FIRST, not the current (spec §12.1).")
            rep.conditions.append(f"the operator explains why {key} changed after {where}")
        else:
            rep.ok(f"{key} first written at {where} == current; {len(logs)} MetadataSet event(s)")


# ── verdict ───────────────────────────────────────────────────────────────────

def render(rep: Report, onchain: bool) -> str:
    if rep.rejects:
        verdict = "REJECT"
        rationale = (f"{len(rep.rejects)} check(s) failed against the ledger; a digest that does not match is a claim that "
                     f"did not survive verification. First failure: {rep.rejects[0]}")
    elif rep.conditions:
        verdict = "APPROVE_WITH_CONDITIONS"
        rationale = ("Every check that could be run here matched the ledger. What could not be run is listed as a "
                     "condition rather than assumed — not yet known is a finding, not an approval.")
    else:
        verdict = "APPROVE"
        rationale = ("Raw-byte digests, the doctrine root over the fifteen pointers, the read-only allowlist, the mirror "
                     "and the card all match the ledger" + (" and the chain" if onchain else "") +
                     ". This proves the BINDING of these files to the ledger; it does not prove who rendered any verdict.")
    rep.risks.append("the doctrine root detects an edit and prevents none: an owner can edit, rerun the binder and publish a "
                     "fresh internally-consistent root — only comparison against the root FIRST written on chain catches it")
    if not onchain:
        rep.risks.append("steps 1-5 only: nothing here was compared to a chain; a ledger and files that agree with each "
                         "other prove consistency, not registration")
    else:
        rep.risks.append("ERC-8004 is Draft (created 2025-08-13); a breaking revision would require re-issuing the card")
    out = ["FINDINGS:"]
    out += [f"  - {f}" for f in rep.findings]
    out.append(f"VERDICT: {verdict}")
    out.append(f"RATIONALE: {rationale}")
    out.append("CONDITIONS:" + ("" if rep.conditions else " none"))
    out += [f"  {i}. {c}" for i, c in enumerate(rep.conditions, 1)]
    out.append("RISKS WATCHED:")
    out += [f"  - {r}" for r in rep.risks]
    return verdict, "\n".join(out)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Verify the Savante binding: recompute every digest against savante.commitments.json.")
    ap.add_argument("repo", nargs="?", type=Path, default=Path("."), help="repo root (default: .)")
    ap.add_argument("--mirror", type=Path, default=sb.DEFAULT_MIRROR, help="mindX mirror path for step 5")
    ap.add_argument("--no-mirror-check", action="store_true", help="skip step 5; recorded as a condition")
    ap.add_argument("--onchain", action="store_true", help="step 6: read the registry over JSON-RPC")
    ap.add_argument("--rpc", help="JSON-RPC URL (required with --onchain; no default)")
    ap.add_argument("--registry", help="ERC-8004 identity registry address (required with --onchain; no default)")
    ap.add_argument("--agent-id", type=int, help="agentId / ERC-721 tokenId (required with --onchain; no default)")
    a = ap.parse_args(argv)
    if a.onchain and (not a.rpc or not a.registry or a.agent_id is None):
        ap.error("--onchain requires --rpc, --registry and --agent-id; none has a default")

    sb.keccak_selftest()
    rep = Report()
    repo = a.repo.resolve()
    ledger_path = repo / sb.LEDGER_NAME
    if not ledger_path.is_file():
        rep.reject(f"{ledger_path} does not exist — there is no ledger to verify against")
        verdict, text = render(rep, a.onchain)
        print(text)
        return EXIT[verdict]
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        rep.reject(f"ledger is not valid JSON: {e}")
        verdict, text = render(rep, a.onchain)
        print(text)
        return EXIT[verdict]

    for f in ledger.get("findings") or []:
        rep.note(f"ledger carries a finding from the binder: {f}")

    persona_bytes = check_artifact(rep, repo, ledger, "identity")               # step 1
    persona: Any = None
    root: Optional[str] = None
    if persona_bytes is not None:
        try:
            persona = json.loads(persona_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            rep.reject(f"savante.persona is not valid JSON: {e}")
    if persona is not None:
        root = check_doctrine_root(rep, persona, ledger)                        # step 2
    charter = check_artifact(rep, repo, ledger, "charter")                      # step 3
    check_artifact(rep, repo, ledger, "skill")
    check_artifact(rep, repo, ledger, "facet_agent")
    check_artifact(rep, repo, ledger, "facet_model")
    if persona is not None:
        check_tools(rep, charter, persona)                                      # step 4
    check_mirror(rep, persona_bytes, a.mirror.resolve(), a.no_mirror_check)     # step 5
    persona_sha = sb.sha256_hex(persona_bytes) if persona_bytes is not None else None
    check_card(rep, repo, ledger, root, persona_sha)
    if a.onchain:
        check_onchain(rep, ledger, root, persona_sha, a.rpc, a.registry, a.agent_id)  # step 6

    verdict, text = render(rep, a.onchain)
    print(text)
    return EXIT[verdict]


if __name__ == "__main__":
    sys.exit(main())
