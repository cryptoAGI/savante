#!/usr/bin/env python3
"""bind/savante_verify.py — the third-party checker. One grep gates both a merge and a purchase.

    python3 bind/savante_verify.py [REPO]                       # steps 1-5, offline, no trust in the author
    python3 bind/savante_verify.py REPO --onchain --rpc URL --registry ADDR --agent-id N   # + step 6

Steps (spec §8):
  0. FIRST, before any digest: the manifest's `algorithms` block against the closed sagi.thot_manifest/1
     vocabulary (sagi/engine/THOT_MANIFEST.md §3a). A missing block, a missing required key, a key outside
     the vocabulary, or any value other than the one implemented here is a REJECT, and nothing else runs.
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

  7. sAGI.prompt's body must equal the charter body BYTE FOR BYTE — the derived facet has not drifted.
  8. Rebuild savante.thot.json: re-hash every facet from raw bytes, rebuild the canonical form, and
     recompute thot: / CID / contentRoot / bundle_root / the 64-leaf Merkle root and compare the §3
     structural fields S1-S11; then check the ledger agrees with the manifest it points at, that the rung
     is not claimed above its evidence, that locator_holds is byte-identical at the locator commit when
     that commit is in the local clone (§6), and the generation / parent / parent_reason per §7 V1-V7
     (V6 against --parent-manifest, or a commit of the local clone; never the network).

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

def check_prompt_derivation(rep: Report, repo: Path) -> None:
    """Step 7 — the derived facet must still derive. The charter is authoritative; sAGI.prompt is a
    copy of its body, and a copy that has drifted is a second source of truth nobody voted for."""
    charter_rel, prompt_rel = ".claude/agents/savante.md", "sAGI.prompt"
    try:
        charter_text = (repo / charter_rel).read_text(encoding="utf-8")
    except OSError as e:
        rep.reject(f"cannot read {charter_rel}: {e}")
        return
    try:
        prompt_text = (repo / prompt_rel).read_text(encoding="utf-8")
    except FileNotFoundError:
        rep.unknown(f"{prompt_rel} is absent — the bundle carries no .prompt facet",
                    f"run bind/savante_bind.py to derive {prompt_rel} from the charter body")
        return

    def body(text: str) -> Optional[str]:
        if not text.startswith("---\n"):
            return None
        try:
            return text[text.index("\n---\n", 3) + len("\n---\n"):]
        except ValueError:
            return None

    want, got = body(charter_text), body(prompt_text)
    if want is None or got is None:
        rep.reject(f"{charter_rel} or {prompt_rel} has no closing frontmatter delimiter")
        return
    if want == got:
        rep.ok(f"{prompt_rel} body is byte-identical to the {charter_rel} body "
               f"({len(want.encode('utf-8'))} B) — the derived facet has not drifted")
    else:
        off = next((i for i, (a, b) in enumerate(zip(want, got)) if a != b), min(len(want), len(got)))
        rep.reject(f"{prompt_rel} has DRIFTED from {charter_rel} at body byte offset {off} "
                   f"(charter body {len(want)} chars, prompt body {len(got)} chars); the charter is authoritative")


def check_algorithms(rep: Report, repo: Path, ledger: Dict[str, Any]) -> bool:
    """Step 0 (THOT_MANIFEST.md §8) — the declared algorithms, before any digest is computed.

    To refuse is to render no APPROVE and exit non-zero (§3a). This verifier implements exactly the
    vocabulary in savante_bind.ALGORITHMS_ALWAYS / ALGORITHMS_CONDITIONAL, shared by import."""
    b = ledger.get("bundle")
    name = (b.get("path") if isinstance(b, dict) else None) or sb.MANIFEST_NAME
    path = repo / name
    if not path.is_file():
        rep.reject(f"{name} is absent, so no `algorithms` block declares which functions the digests were "
                   "computed with; refusing before any digest (§3a rule 1a)")
        return False
    try:
        manifest = sb.loads_strict(path.read_bytes().decode("utf-8"))
    except ValueError as e:  # UnicodeDecodeError, JSONDecodeError and sb.DuplicateKey are all ValueErrors
        rep.reject(f"{name} is not valid UTF-8 JSON with unique keys, so its `algorithms` block cannot be "
                   f"read unambiguously: {e}")
        return False
    refusals = sb.algorithms_refusals(manifest)
    if refusals:
        for r in refusals:
            rep.reject(f"{name}: {r}. Refusing to verify — a digest checked with the wrong function is not a check.")
        return False
    declared = sorted(k for k in manifest["algorithms"] if k not in sb.ALGORITHMS_RESERVED)
    rep.ok(f"{name} declares exactly the sagi.thot_manifest/1 algorithms this verifier implements "
           f"({len(declared)} keys: {', '.join(declared)}); checked before any digest")
    return True


def facet_slot_problems(manifest: Dict[str, Any]) -> List[str]:
    """§5: a slot belongs to a facet whose state is "present"; absent facets take none. A facets[] entry that
    is not an object, has any other state, repeats a name, or is also listed in absent[] makes the slot
    set ambiguous, so it is refused rather than guessed at."""
    out: List[str] = []
    facets = manifest.get("facets")
    if not isinstance(facets, list):
        return ["`facets` is missing or is not a list"]
    absent = {a.get("facet") for a in (manifest.get("absent") or []) if isinstance(a, dict)}
    seen: set = set()
    for i, f in enumerate(facets):
        if not isinstance(f, dict):
            out.append(f"facets[{i}] is not an object")
            continue
        name = f.get("facet")
        if f.get("state") != "present":
            out.append(f"facets[{i}] `{name}` has state {f.get('state')!r}; §5 gives a slot only to state "
                       "\"present\", and an absent facet belongs in absent[], not facets[]")
        if name in absent:
            out.append(f"facet `{name}` is listed in both facets[] and absent[]")
        if name in seen:
            out.append(f"facet `{name}` appears twice in facets[]")
        seen.add(name)
    return out


BUNDLE_ROOT_KEYS = {"value", "hash", "order", "preimage_bytes", "construction", "note"}
MERKLE_KEYS = {"leaves", "leaf_rule", "padding", "populated", "root", "ternary_head", "ternary_head_index", "why", "note"}


def _int(v: Any) -> bool:
    """§3 'integer': a JSON number with an integer value, never a boolean."""
    return isinstance(v, int) and not isinstance(v, bool)


def structural_problems(manifest: Dict[str, Any], order: List[str], preimage_len: int) -> Tuple[List[str], List[str]]:
    """§3 S2-S4 and S6-S11 (S1 and S5 are the recomputed roots, compared by the caller), plus at_locator.
    Returns (refusals, findings)."""
    out: List[str] = []
    notes: List[str] = []
    br = manifest.get("bundle_root") if isinstance(manifest.get("bundle_root"), dict) else {}
    mk = manifest.get("merkle") if isinstance(manifest.get("merkle"), dict) else {}
    algs = manifest.get("algorithms") if isinstance(manifest.get("algorithms"), dict) else {}
    if br.get("hash") != algs.get("bundle_root") or not isinstance(br.get("hash"), str):
        out.append(f"S2 bundle_root.hash {br.get('hash')!r} != algorithms.bundle_root {algs.get('bundle_root')!r}")
    if br.get("order") != order:
        out.append(f"S3 bundle_root.order {br.get('order')!r} != the §5 order of the present facets {order}")
    if not (_int(br.get("preimage_bytes")) and br["preimage_bytes"] == preimage_len):
        out.append(f"S4 bundle_root.preimage_bytes {br.get('preimage_bytes')!r} != {preimage_len}")
    for label, key, want in (("S6", "leaves", sb.MERKLE_LEAVES), ("S7", "populated", len(order)),
                             ("S9", "ternary_head_index", 0)):
        if not (_int(mk.get(key)) and mk[key] == want):
            out.append(f"{label} merkle.{key} {mk.get(key)!r} != {want}")
    if mk.get("ternary_head") != "persona":
        out.append(f"S8 merkle.ternary_head {mk.get('ternary_head')!r} != 'persona'")
    ev = ((manifest.get("rung") or {}).get("evidence") if isinstance(manifest.get("rung"), dict) else None) or {}
    loc = ev.get("locator") if isinstance(ev, dict) else None
    if not (isinstance(loc, str) and sb.LOCATOR_RE.match(loc)):
        out.append(f"S10 rung.evidence.locator {loc!r} is not <host>/<owner>/<repo>@<40 lowercase hex>")
    holds = ev.get("locator_holds") if isinstance(ev, dict) else None
    if not (isinstance(holds, list) and all(isinstance(h, str) for h in holds) and len(set(holds)) == len(holds)
            and all(h in order for h in holds) and holds == [f for f in order if f in holds]):
        out.append(f"S11 rung.evidence.locator_holds {holds!r} is not a list of distinct present facets in "
                   "bundle_root.order order")
    else:
        for f in manifest.get("facets") or []:
            if isinstance(f, dict) and "at_locator" in f and f["at_locator"] is not (f.get("facet") in holds):
                out.append(f"facet `{f.get('facet')}` at_locator {f['at_locator']!r} disagrees with locator_holds (§3)")
    for name, blk, allowed in (("bundle_root", br, BUNDLE_ROOT_KEYS), ("merkle", mk, MERKLE_KEYS)):
        extra = sorted(set(blk) - allowed)
        if extra:
            notes.append(f"{name} carries keys outside §3: {extra}")
    return out, notes


def lineage_problems(manifest: Dict[str, Any]) -> List[str]:
    """§7 V1-V5, offline and without P."""
    out: List[str] = []
    b = manifest.get("bundle") if isinstance(manifest.get("bundle"), dict) else {}
    gen, parent, reason = b.get("generation"), b.get("parent"), b.get("parent_reason")
    if not (_int(gen) and gen >= 1):
        out.append(f"V1 bundle.generation {gen!r} is not an integer >= 1")
    elif (gen == 1) != (parent is None):
        out.append(f"V2 generation {gen} with parent {parent!r}: generation is 1 exactly when parent is null")
    elif gen >= 2:
        if not (isinstance(parent, str) and sb.CID_RE.match(parent)):
            out.append(f"V3 bundle.parent {parent!r} is not a ^bafkrei[a-z2-7]{{52}}$ CID")
        elif parent == (manifest.get("identity") or {}).get("cid"):
            out.append("V3 bundle.parent is the manifest's own identity.cid")
    if not (isinstance(reason, str) and reason):
        out.append(f"V4 bundle.parent_reason {reason!r} is not a non-empty string")
    if "lineage" in manifest:
        out.append("V5 the manifest carries a top-level `lineage` key; a persona's lineage is never a THOT parent")
    return out


IDENTITY_SCOPE = ("cid", "identity_thot", "identity_content_root", "canonicalisation")


def parent_problems(manifest: Dict[str, Any], p: Any) -> List[str]:
    """§7 V6 with P's bytes on disk: recompute P's identity.cid under identity-only scope (§3a rule 3)."""
    if not isinstance(p, dict):
        return ["V6 P is not a JSON object"]
    b = manifest.get("bundle") or {}
    pa = p.get("algorithms") if isinstance(p.get("algorithms"), dict) else {}
    known = sb.ALGORITHMS_ALWAYS
    out = [f"V6 P declares algorithms.{k} = {pa.get(k)!r}; identity-only scope implements {known[k]!r}"
           for k in IDENTITY_SCOPE if pa.get(k) != known[k]]
    if out:
        return out
    if sb.manifest_identity_cid(p) != b.get("parent"):
        out.append(f"V6 P's recomputed identity.cid {sb.manifest_identity_cid(p)} != bundle.parent {b.get('parent')}")
    pb = p.get("bundle") if isinstance(p.get("bundle"), dict) else {}
    if pb.get("id") != b.get("id"):
        out.append(f"V6 P's bundle.id {pb.get('id')!r} != bundle.id {b.get('id')!r}")
    if not (_int(pb.get("generation")) and _int(b.get("generation")) and pb["generation"] == b["generation"] - 1):
        out.append(f"V6 P's bundle.generation {pb.get('generation')!r} != {b.get('generation')!r} - 1")
    return out


def find_parent_in_clone(repo: Path, cid: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """V6 from 'a commit in a clone already on disk': walk LOCAL history of the manifest path for a file whose
    recomputed identity.cid equals `cid`. Never fetches (V7); a shallow or absent clone simply finds nothing."""
    log = sb.git(repo, "log", "--format=%H", "--", sb.MANIFEST_NAME)
    for commit in (log or "").splitlines():
        raw = sb.git_bytes(repo, commit, sb.MANIFEST_NAME)
        try:
            m = sb.loads_strict(raw.decode("utf-8")) if raw is not None else None
        except ValueError:
            continue
        if isinstance(m, dict) and sb.manifest_identity_cid(m) == cid:
            return m, commit
    return None, None


def check_lineage(rep: Report, repo: Path, manifest: Dict[str, Any], name: str, parent_manifest: Optional[Path]) -> None:
    """§8 step 7: bundle.generation, bundle.parent and bundle.parent_reason per §7 V1-V7."""
    problems = lineage_problems(manifest)
    if problems:
        for p in problems:
            rep.reject(f"{name}: {p}")
        return
    b = manifest["bundle"]
    if b["generation"] == 1:
        rep.ok(f"{name} is generation 1 (genesis): parent null, parent_reason stated — §7 V1-V5")
        return
    rep.ok(f"{name} is generation {b['generation']}, parent {b['parent']}, parent_reason stated — §7 V1-V5")
    if parent_manifest is not None:
        try:
            p = sb.loads_strict(parent_manifest.read_bytes().decode("utf-8"))
        except (OSError, ValueError) as e:
            rep.reject(f"--parent-manifest {parent_manifest} unreadable as UTF-8 JSON with unique keys: {e}")
            return
        where = str(parent_manifest)
    else:
        p, commit = find_parent_in_clone(repo, b["parent"])
        where = f"{sb.MANIFEST_NAME} @ {commit}" if commit else None
    if p is None:
        rep.note(f"{name} parent {b['parent']} NOT VERIFIED: P's bytes are not on this host (no --parent-manifest, and "
                 "no commit of this clone holds a manifest with that CID). Not a pass and not a refusal (§7 V6); "
                 "this verifier never follows the network to find P (V7)")
        return
    pp = parent_problems(manifest, p)
    if pp:
        for x in pp:
            rep.reject(f"{name}: {x} (P read from {where})")
        return
    rep.ok(f"{name} parent verified offline against {where}: P recomputes to {b['parent']}, bundle.id "
           f"{b['id']!r}, generation {p['bundle']['generation']} = {b['generation']} - 1 (§7 V6, identity-only scope)")


def check_locator_bytes(rep: Report, repo: Path, manifest: Dict[str, Any], name: str) -> None:
    """§6 SHOULD: every facet in locator_holds is byte-identical at the locator commit, when that commit is in the
    local clone. Never fetched; a commit this clone lacks is a finding, not a refusal."""
    ev = (manifest.get("rung") or {}).get("evidence") or {}
    commit = str(ev.get("locator", "")).rsplit("@", 1)[-1]
    holds = ev.get("locator_holds") or []
    if sb.git(repo, "cat-file", "-e", f"{commit}^{{commit}}") is None:
        rep.note(f"{name} locator commit {commit} is not in a local clone here; locator_holds {holds} not checked "
                 "against it (§6)")
        return
    facets = {f.get("facet"): f for f in manifest.get("facets") or [] if isinstance(f, dict)}
    bad = [h for h in holds if (lambda raw: raw is None or sb.sha256_hex(raw) != facets[h].get("sha256"))(
        sb.git_bytes(repo, commit, str(facets[h].get("path"))))]
    if bad:
        rep.reject(f"{name}: locator_holds lists {bad}, whose bytes at {commit} do not hash to the manifest sha256 (§6)")
    else:
        rep.ok(f"{name}: all {len(holds)} facet(s) in locator_holds are byte-identical at locator commit {commit[:12]} (§6)")


def check_components(rep: Report, persona: Any, ledger: Dict[str, Any]) -> None:
    """The persona's /token/intelligence/components names exactly the components the ledger binds."""
    try:
        comps = sb.resolve(persona, "/token/intelligence/components")
    except sb.PointerMissing as e:
        rep.reject(f"persona component list missing: {e}")
        return
    declared = sorted((c.get("component"), c.get("path")) for c in comps if isinstance(c, dict)) \
        if isinstance(comps, list) else []
    arts = ledger.get("artifacts") if isinstance(ledger.get("artifacts"), dict) else {}
    ledgered = sorted((k, v.get("path")) for k, v in arts.items() if isinstance(v, dict))
    if not isinstance(comps, list) or len(declared) != len(comps) or declared != ledgered:
        rep.reject(f"persona /token/intelligence/components {declared} != the ledgered components {ledgered}")
    else:
        rep.ok(f"persona /token/intelligence/components names exactly the {len(ledgered)} ledgered components")


def check_bundle(rep: Report, repo: Path, ledger: Dict[str, Any], parent_manifest: Optional[Path] = None) -> None:
    """Step 8 — rebuild the THOT manifest from raw bytes and recompute all four names.

    This is the check that makes the bundle mean anything: every facet re-hashed from disk, the
    canonical form rebuilt, and thot / cid / contentRoot / bundle_root / merkle recomputed. No
    network, no trust in the author."""
    b = ledger.get("bundle")
    if not isinstance(b, dict):
        rep.unknown("the ledger carries no `bundle` block — it predates the facet bundle",
                    "re-run bind/savante_bind.py to emit savante.thot.json and its ledger block")
        return
    path = repo / b.get("path", sb.MANIFEST_NAME)
    if not path.is_file():
        rep.reject(f"the ledger records a bundle but {path.name} does not exist")
        return
    raw = path.read_bytes()
    if b.get("bytes") is not None and len(raw) != b["bytes"]:
        rep.reject(f"{path.name}: {len(raw)} B on disk, ledger says {b['bytes']} B")
        return
    try:
        manifest = sb.loads_strict(raw.decode("utf-8"))
    except ValueError as e:
        rep.reject(f"{path.name} is not valid UTF-8 JSON with unique keys: {e}")
        return

    ident = manifest.get("identity")
    if not isinstance(ident, dict):
        rep.reject(f"{path.name} has no `identity` block")
        return

    # HASH AGILITY — enforced at step 0 (check_algorithms), before any digest. Belt and braces: a
    # manifest that changed between step 0 and here is refused again rather than verified.
    if sb.algorithms_refusals(manifest):
        rep.reject(f"{path.name}: the algorithms block no longer passes §3a at step 8; refusing")
        return

    # 8a. the manifest's own identity, over the document WITHOUT that block.
    canon = sb.canonical_bytes({k: v for k, v in manifest.items() if k != "identity"})
    sha = sb.sha256_hex(canon)
    cid, _reason = sb.cid_or_none(canon)
    problems: List[str] = []
    if ident.get("thot") != "thot:" + sha:
        problems.append(f"thot: recomputed thot:{sha}, manifest says {ident.get('thot')}")
    if ident.get("cid") != cid:
        problems.append(f"cid: recomputed {cid}, manifest says {ident.get('cid')}")
    if ident.get("contentRoot") != "0x" + sb.keccak256(canon).hex():
        problems.append(f"contentRoot: recomputed 0x{sb.keccak256(canon).hex()}, manifest says {ident.get('contentRoot')}")
    if ident.get("canonical_bytes") != len(canon):
        problems.append(f"canonical_bytes: recomputed {len(canon)}, manifest says {ident.get('canonical_bytes')}")

    # 8b. every facet re-hashed from its raw bytes, then the two roots. §5: only state "present" takes a
    # slot, so any other entry in facets[] is refused rather than silently given (or denied) one.
    problems += facet_slot_problems(manifest)
    by_facet = {f.get("facet"): f for f in manifest.get("facets", [])
                if isinstance(f, dict) and f.get("state") == "present"}
    preimage, leaves = b"", []
    for ext in sb.FACET_ORDER:
        f = by_facet.get(ext)
        if f is None:
            problems.append(f"manifest is missing the required facet `{ext}`")
            continue
        fp = repo / f["path"]
        if not fp.is_file():
            problems.append(f"facet `{ext}`: {f['path']} does not exist")
            continue
        data = fp.read_bytes()
        got_sha = sb.sha256_hex(data)
        if got_sha != f.get("sha256") or len(data) != f.get("bytes"):
            problems.append(f"facet `{ext}` ({f['path']}): {len(data)} B sha256 {got_sha} — manifest says "
                            f"{f.get('bytes')} B sha256 {f.get('sha256')}")
            continue
        piece = ext.encode("utf-8") + sb.US + got_sha.encode("ascii")
        preimage += piece + sb.RS
        leaves.append(sb.keccak256(piece))

    got_bundle_root = "0x" + sb.keccak256(preimage).hex()
    want_bundle_root = (manifest.get("bundle_root") or {}).get("value")
    if got_bundle_root != want_bundle_root:
        problems.append(f"bundle_root: recomputed {got_bundle_root}, manifest says {want_bundle_root}")
    extra = sorted(str(f.get("facet")) for f in manifest.get("facets", [])
                   if isinstance(f, dict) and f.get("state") == "present" and f.get("facet") not in sb.FACET_ORDER)
    if extra or manifest.get("custom"):
        problems.append(f"present facets outside this verifier's registry order {extra} or custom facets "
                        f"{manifest.get('custom')}: §5 would give them slots this verifier does not compute")
    try:
        got_merkle: Optional[str] = sb.merkle_root(leaves)
    except ValueError as e:
        got_merkle = None
        problems.append(f"merkle: {e}")
    want_merkle = (manifest.get("merkle") or {}).get("root")
    if got_merkle is not None and got_merkle != want_merkle:
        problems.append(f"merkle root: recomputed {got_merkle}, manifest says {want_merkle}")
    # §8 step 4: the structural fields beside the two roots (§3 S2-S4, S6-S11).
    s_problems, s_notes = structural_problems(manifest, [ext for ext in sb.FACET_ORDER if ext in by_facet], len(preimage))
    problems += s_problems
    for n in s_notes:
        rep.note(f"{path.name}: {n}")

    # 8c. the ledger must agree with the manifest it points at.
    if b.get("identity", {}).get("thot") not in (None, ident.get("thot")):
        problems.append(f"ledger bundle.identity.thot {b['identity']['thot']} != manifest {ident.get('thot')}")
    if b.get("bundle_root") not in (None, want_bundle_root):
        problems.append(f"ledger bundle_root {b.get('bundle_root')} != manifest {want_bundle_root}")

    if problems:
        for p in problems:
            rep.reject(f"{path.name}: {p}")
        return

    rep.ok(f"{path.name}: {len(by_facet)} facets re-hashed from raw bytes; bundle_root {got_bundle_root}; "
           f"merkle {got_merkle} over {len(leaves)}/{sb.MERKLE_LEAVES} leaves; structural fields S1-S11 match")
    rep.ok(f"{path.name} identity reproduces from its own canonical bytes ({len(canon)} B): {ident.get('thot')}, "
           f"cid {ident.get('cid')}, contentRoot {ident.get('contentRoot')}")

    rung = (manifest.get("rung") or {}).get("value")
    ev = (manifest.get("rung") or {}).get("evidence") or {}
    if rung == "referenced" and not (ev.get("commitTx") or ev.get("dataTx") or ev.get("attestation")):
        rep.ok(f"{path.name} rung is `referenced` with no commit/data/attestation evidence — the honest rung "
               "for a bundle that has been published nowhere")
    elif rung != "referenced" and not (ev.get("dataTx") or ev.get("commitTx")):
        rep.reject(f"{path.name} claims rung `{rung}` with no transaction evidence")
    check_locator_bytes(rep, repo, manifest, path.name)                        # §6
    check_lineage(rep, repo, manifest, path.name, parent_manifest)             # §8 step 7 — §7 V1-V7


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
    ap.add_argument("--parent-manifest", type=Path, default=None,
                    help="P's bytes for §7 V6 (a local file). Without it, P is looked for in this clone's LOCAL git "
                         "history; never fetched. Not found = the parent is reported NOT VERIFIED, not refused")
    ap.add_argument("--self-test", action="store_true",
                    help="run the step-0 refusal cases, condition G, §3 S / §7 V unit cases, and the ui.py sharing check, and exit")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
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
        ledger = sb.loads_strict(ledger_path.read_text(encoding="utf-8"))
    except ValueError as e:
        rep.reject(f"ledger is not valid JSON with unique keys: {e}")
        verdict, text = render(rep, a.onchain)
        print(text)
        return EXIT[verdict]

    for f in ledger.get("findings") or []:
        rep.note(f"ledger carries a finding from the binder: {f}")

    if not check_algorithms(rep, repo, ledger):                                 # step 0 — before any digest
        verdict, text = render(rep, a.onchain)
        print(text)
        return EXIT[verdict]

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
    for extra in ("facet_prompt", "facet_tool", "facet_voaice", "facet_faice"):
        if extra in (ledger.get("artifacts") or {}):
            check_artifact(rep, repo, ledger, extra)
    if persona is not None:
        check_tools(rep, charter, persona)                                      # step 4
        check_components(rep, persona, ledger)
    check_mirror(rep, persona_bytes, a.mirror.resolve(), a.no_mirror_check)     # step 5
    persona_sha = sb.sha256_hex(persona_bytes) if persona_bytes is not None else None
    check_card(rep, repo, ledger, root, persona_sha)
    check_prompt_derivation(rep, repo)                                          # step 7
    check_bundle(rep, repo, ledger, a.parent_manifest)                          # step 8 (+ §6, §7)
    if a.onchain:
        check_onchain(rep, ledger, root, persona_sha, a.rpc, a.registry, a.agent_id)  # step 6

    verdict, text = render(rep, a.onchain)
    print(text)
    return EXIT[verdict]


def self_test() -> int:
    """Step 0 end to end: each refusal case is written to a scratch directory (never the repo) and run
    through main(); it must REJECT, exit non-zero, and compute no digest. Then ui.py's inlined copy of
    the vocabulary must equal savante_bind's."""
    import ast
    import contextlib
    import io
    import tempfile

    ok = True

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        ok = ok and cond
        print(f"[{'PASS' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")

    base: Dict[str, Any] = {"schema": "sagi.thot_manifest/1", "algorithms": sb.manifest_algorithms(),
                            "doctrine_root": "0x" + "00" * 32, "facets": [], "custom": []}

    def run(manifest_text: Optional[str]) -> Tuple[int, str]:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / sb.LEDGER_NAME).write_text(json.dumps({"bundle": {"path": sb.MANIFEST_NAME}}), encoding="utf-8")
            if manifest_text is not None:
                (p / sb.MANIFEST_NAME).write_text(manifest_text, encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = main([str(p), "--no-mirror-check"])
            return code, buf.getvalue()

    def mutated(fn: Any) -> str:
        m = json.loads(json.dumps(base))
        fn(m)
        return json.dumps(m)

    code, out = run(json.dumps(base))
    check("control: the emitted block passes step 0", "declares exactly the sagi.thot_manifest/1" in out
          and "§3a" not in out)

    cases: List[Tuple[str, Optional[str]]] = [
        ("manifest file absent", None),
        ("manifest not JSON", "{not json"),
        ("algorithms block missing", mutated(lambda m: m.pop("algorithms"))),
        ("algorithms block not an object", mutated(lambda m: m.__setitem__("algorithms", "sha256"))),
        ("unknown key facet_digest_v2", mutated(lambda m: m["algorithms"].__setitem__("facet_digest_v2", "blake3"))),
        ("doctrine_root key missing while the manifest has a doctrine_root",
         mutated(lambda m: m["algorithms"].pop("doctrine_root"))),
        ("doctrine_root = sha3-256", mutated(lambda m: m["algorithms"].__setitem__("doctrine_root", "sha3-256"))),
        ("canonicalisation without .encode('utf-8')", mutated(lambda m: m["algorithms"].__setitem__(
            "canonicalisation", "json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=False)"))),
        ("git_blob missing while a facet is named by a git blob",
         mutated(lambda m: m["facets"].append({"facet": "voaice", "state": "present", "git_blob": "0" * 40}))),
        ("G +1 git_blob missing while facets[0].reference.git_blob_sha1 names the voice",
         mutated(lambda m: m["facets"].append({"facet": "voaice", "reference": {"git_blob_sha1": "bf" * 20}}))),
        ("G +3 git_blob missing while custom[0].source.git_blob_id is present",
         mutated(lambda m: m["custom"].append({"facet": "x-a.b", "source": {"git_blob_id": None}}))),
        ("schema missing", mutated(lambda m: m.pop("schema"))),
        ("schema sagi.thot_manifest/2", mutated(lambda m: m.__setitem__("schema", "sagi.thot_manifest/2"))),
        ("note is not a string", mutated(lambda m: m["algorithms"].__setitem__("note", {"x": 1}))),
        ("duplicate merkle_pad key in the raw bytes (last value keccak256)",
         json.dumps(base).replace('"merkle_pad": "keccak256"',
                                  '"merkle_pad": "sha3-256", "merkle_pad": "keccak256"', 1)),
    ]
    for k in sb.ALGORITHMS_ALWAYS:
        cases.append((f"{k} missing", mutated(lambda m, k=k: m["algorithms"].pop(k))))
        cases.append((f"{k} = blake3", mutated(lambda m, k=k: m["algorithms"].__setitem__(k, "blake3"))))
    for label, text in cases:
        code, out = run(text)
        verdict_line = next((ln for ln in out.splitlines() if ln.startswith("VERDICT:")), "")
        check(f"refused: {label}", code != 0 and verdict_line == "VERDICT: REJECT"
              and "ledger has no artifacts" not in out and "KNOWN" not in out,
              f"exit {code}, {verdict_line}")

    # §5 slots: only state "present" takes one (unit cases on facet_slot_problems, used by step 8).
    present = {"facets": [{"facet": "persona", "state": "present"}, {"facet": "faice", "state": "present"}],
               "absent": [{"facet": "reputation", "state": "absent"}]}
    check("slots: all-present facets[] passes", facet_slot_problems(present) == [])
    for label, fn in [
        ("a facets[] entry with state absent", lambda m: m["facets"][1].__setitem__("state", "absent")),
        ("a facets[] entry with no state", lambda m: m["facets"][1].pop("state")),
        ("a facet in both facets[] and absent[]", lambda m: m["absent"].append({"facet": "faice"})),
        ("a facet named twice in facets[]", lambda m: m["facets"].append({"facet": "persona", "state": "present"})),
        ("facets not a list", lambda m: m.__setitem__("facets", {"persona": {}})),
    ]:
        m = json.loads(json.dumps(present))
        fn(m)
        r = facet_slot_problems(m)
        check(f"slots refused: {label}", bool(r), r[0] if r else "NOT refused")

    # Condition G negatives end to end: step 0 must pass (the spec forbids widening G).
    for label, fn in [
        ("G -1 facets[0].reference.commit = 40 hex", lambda m: m["facets"].append({"reference": {"commit": "3f" * 20}})),
        ("G -4 facets[0].oid = 40 hex and reference.git_object", lambda m: m["facets"].append(
            {"oid": "ab" * 20, "reference": {"git_object": "cd" * 20}})),
        ("G -5 top-level references[0].git_blob_sha1 and absent[0].git_blob_sha1", lambda m: (
            m.__setitem__("references", [{"git_blob_sha1": "ab" * 20}]), m.__setitem__("absent", [{"git_blob_sha1": "x"}]))),
        ("G -7 facets[0].note = 'git_blob_sha1 bfcc5e…'", lambda m: m["facets"].append({"note": "git_blob_sha1 bfcc5e"})),
        ("G substring: facets[0].x_git_blob", lambda m: m["facets"].append({"x_git_blob": "ab" * 20})),
    ]:
        code, out = run(mutated(fn))
        check(f"step 0 passes: {label}", "declares exactly the sagi.thot_manifest/1" in out and "§3a" not in out)

    # §3 S2-S11 and §7 V1-V6, unit cases on the pure functions step 8 uses.
    order = list(sb.FACET_ORDER)
    loc = "github.com/cryptoAGI/savante@" + "1f" * 20
    good_s = {"algorithms": sb.manifest_algorithms(),
              "bundle_root": {"value": "0x", "hash": "keccak256", "order": order, "preimage_bytes": 571, "construction": "c"},
              "merkle": {"leaves": 64, "populated": 8, "root": "0x", "ternary_head": "persona", "ternary_head_index": 0},
              "facets": [{"facet": f, "at_locator": True} for f in order],
              "rung": {"evidence": {"locator": loc, "locator_holds": order}}}
    check("S: a well-formed manifest passes", structural_problems(good_s, order, 571) == ([], []),
          str(structural_problems(good_s, order, 571)))
    for label, fn in [
        ("S2 hash differs from algorithms.bundle_root", lambda m: m["bundle_root"].__setitem__("hash", "sha256")),
        ("S3 order reversed", lambda m: m["bundle_root"].__setitem__("order", order[::-1])),
        ("S4 preimage_bytes true-ish boolean", lambda m: m["bundle_root"].__setitem__("preimage_bytes", True)),
        ("S6 leaves as the string '64'",lambda m: m["merkle"].__setitem__("leaves", "64")),
        ("S7 populated 9", lambda m: m["merkle"].__setitem__("populated", 9)),
        ("S8 ternary_head agent", lambda m: m["merkle"].__setitem__("ternary_head", "agent")),
        ("S9 ternary_head_index false", lambda m: m["merkle"].__setitem__("ternary_head_index", False)),
        ("S10 short commit", lambda m: m["rung"]["evidence"].__setitem__("locator", "github.com/cryptoAGI/savante@1fcca89")),
        ("S11 locator_holds out of order", lambda m: m["rung"]["evidence"].__setitem__("locator_holds", ["agent", "persona"])),
        ("S11 locator_holds names an absent facet", lambda m: m["rung"]["evidence"].__setitem__("locator_holds", ["reputation"])),
        ("at_locator true for a facet not in locator_holds", lambda m: m["rung"]["evidence"].__setitem__("locator_holds", order[1:])),
    ]:
        m = json.loads(json.dumps(good_s))
        fn(m)
        r = structural_problems(m, order, 571)[0]
        check(f"S refused: {label}", bool(r), r[0] if r else "NOT refused")
    m = json.loads(json.dumps(good_s))
    m["merkle"]["extra"] = 1
    check("S: an unknown merkle key is a finding, not a refusal", structural_problems(m, order, 571)[0] == []
          and bool(structural_problems(m, order, 571)[1]))

    p1 = {"schema": sb.SCHEMA, "algorithms": sb.manifest_algorithms(),
          "bundle": {"id": "sAGI", "generation": 1, "parent": None, "parent_reason": "genesis"}, "facets": []}
    p1["identity"] = {"cid": sb.manifest_identity_cid(p1)}
    g2 = {"bundle": {"id": "sAGI", "generation": 2, "parent": p1["identity"]["cid"], "parent_reason": "persona edited"},
          "identity": {"cid": "bafkrei" + "c" * 52}}
    check("V: generation 1 genesis passes", lineage_problems(p1) == [])
    check("V: generation 2 with a CID parent passes", lineage_problems(g2) == [])
    for label, fn in [
        ("V1 generation true", lambda m: m["bundle"].__setitem__("generation", True)),
        ("V1 generation 0", lambda m: m["bundle"].__setitem__("generation", 0)),
        ("V2 generation 1 with a parent", lambda m: m["bundle"].__setitem__("generation", 1)),
        ("V2 generation 2 with parent null", lambda m: m["bundle"].__setitem__("parent", None)),
        ("V3 parent not a bafkrei CID", lambda m: m["bundle"].__setitem__("parent", "thot:" + "a" * 64)),
        ("V3 parent is its own identity.cid", lambda m: m["identity"].__setitem__("cid", m["bundle"]["parent"])),
        ("V4 parent_reason empty", lambda m: m["bundle"].__setitem__("parent_reason", "")),
        ("V5 top-level lineage", lambda m: m.__setitem__("lineage", [])),
    ]:
        m = json.loads(json.dumps(g2))
        fn(m)
        check(f"V refused: {label}", bool(lineage_problems(m)))
    check("V6 P recomputes to parent, same id, generation n-1: passes", parent_problems(g2, p1) == [],
          str(parent_problems(g2, p1)))
    for label, fn in [
        ("V6 P edited so its CID no longer equals parent", lambda p: p["bundle"].__setitem__("parent_reason", "edited")),
        ("V6 P of another bundle", lambda p: p["bundle"].__setitem__("id", "jaimla")),
        ("V6 P declares a cid algorithm outside identity-only scope", lambda p: p["algorithms"].__setitem__("cid", "blake3")),
    ]:
        p = json.loads(json.dumps(p1))
        fn(p)
        check(f"V6 refused: {label}", bool(parent_problems(g2, p)))
    g3 = json.loads(json.dumps(g2))
    g3["bundle"]["generation"] = 3
    check("V6 refused: P's generation is not n-1", bool(parent_problems(g3, p1)))

    # ui.py shares savante_bind's vocabulary and condition G; it must not carry its own copy.
    ui = Path(__file__).resolve().parent.parent / "ui.py"
    if ui.is_file():
        tree = ast.parse(ui.read_text(encoding="utf-8"))
        own = [n.targets[0].id for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
               and isinstance(n.targets[0], ast.Name) and "ALGORITHMS" in n.targets[0].id]
        own += [n.name for n in tree.body if isinstance(n, ast.FunctionDef) and "git" in n.name]
        check("ui.py carries no copy of the vocabulary or of condition G", own == [], str(own))
        import importlib.util
        spec = importlib.util.spec_from_file_location("savante_ui_selftest", ui)
        try:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        except Exception as e:  # noqa: BLE001
            print(f"[SKIP] ui.py not importable here ({e}); behavioural sharing not checked")
            mod = None
        if mod is not None:
            with tempfile.TemporaryDirectory() as d:
                for label, fn, refused in [
                    ("G +1 refused", lambda m: m["facets"].append({"reference": {"git_blob_sha1": "ab" * 20}}), True),
                    ("G -1 reference.commit accepted", lambda m: m["facets"].append({"reference": {"commit": "3f" * 20}}), False),
                    ("G -5 references[].git_blob_sha1 accepted", lambda m: m.__setitem__("references", [{"git_blob_sha1": "x"}]), False),
                ]:
                    (Path(d) / sb.MANIFEST_NAME).write_text(mutated(fn), encoding="utf-8")
                    st = mod.manifest_check(Path(d)).get("state")
                    check(f"ui.manifest_check agrees with savante_bind: {label}", (st == "refused") is refused, str(st))
    else:
        print("[SKIP] ui.py not beside bind/; sharing not checked")

    print("self-test:", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
