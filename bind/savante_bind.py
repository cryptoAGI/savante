#!/usr/bin/env python3
"""bind/savante_bind.py — the OPERATOR's binder. Savante audits this file and never runs it.

Derives, from savante.persona, the two .claude/ files and the six sAGI class facets
(sAGI.agent, sAGI.model, sAGI.prompt, sAGI.tool, sAGI.voaice, sAGI.faice — nine components), the three
DERIVED artifacts:

    savante.agentcard.json    — the public face (EIP-721 metadata + ERC-8004 registration-v1)
    savante.commitments.json  — the integrity ledger (raw-byte digests + the doctrine root)
    savante.thot.json         — the THOT manifest (sagi.thot_manifest/1: facets, algorithms, roots, identity)

Rules this program enforces on itself:

  * stdlib only for sha256 and CIDv1. `cid_v1_raw` is reproduced VERBATIM from
    /home/hacker/mindX/mindx/godel/mindxtrain/inft_publish.py:39-47 (its helper `_b32_lower`
    from :34-36). A CID is emitted only for blobs <= 256 KiB — the bound that function's own
    docstring states (inft_publish.py:40-43); larger blobs are referenced by sha256 only.
  * keccak256 via pycryptodome (Crypto.Hash.keccak), eth_utils.keccak as fallback, and a
    startup self-test keccak256(b"") == c5d2...a470. hashlib.sha3_256 is NIST SHA-3, not
    keccak, and is never used.
  * PREFLIGHT, fail closed: P1 every property name is ASCII; P2 every JSON number is an
    integer (and within +/-2^53, so ECMAScript and Python print it identically). Only under
    P1+P2 does `canonical_bytes` equal RFC 8785 (JCS) output; outside them this program
    refuses to emit any digest and prints the offending RFC 6901 pointer and the reason.
  * MIRROR CHECK, fail closed: md5 of the repo persona must equal md5 of the mindX mirror.
    Overridable with --mirror; skippable ONLY with --no-mirror-check, which is recorded in
    the output as a finding.
  * The doctrine root is keccak256 over the ordered concatenation of the fifteen pointers
    in spec order; a missing pointer is a hard error, never a skipped term.
  * NEVER writes savante.persona. NO network. No wall-clock timestamps: the provenance
    stamp is the git HEAD commit and that commit's date, so two runs over unchanged inputs
    produce byte-identical outputs.
  * Every slot whose value this program did not compute or read is explicit null with a
    stated reason. Nothing here is a claim about anything minted.
  * GENERATIONS (sagi/engine/THOT_MANIFEST.md §7), from LOCAL git only: without --parent-commit the
    manifest committed at HEAD is carried forward and a facet change is refused (G5); with
    --parent-commit REV --parent-reason TEXT, P = savante.thot.json at REV, generation = P's + 1
    and bundle.parent = P's own identity.cid, which P's file must reproduce.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ── constants ─────────────────────────────────────────────────────────────────

KECCAK_EMPTY_HEX = "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
CID_MAX_BYTES = 256 * 1024          # inft_publish.py:40-43 — the single-block bound
INT_SAFE_BOUND = 2 ** 53            # ECMAScript Number integer range, for P2

ERC8004_TYPE = "https://eips.ethereum.org/EIPS/eip-8004#registration-v1"
ERC8004_STATUS = "Draft (created 2025-08-13); local copy of the draft text read 2026-09-03"
ERC8004_REGISTRATIONS_QUOTE = (
    "Agents SHOULD have at least one registration (multiple are possible), and all "
    "fields in the registration are mandatory."
)
ERC8004_SUPPORTEDTRUST_QUOTE = (
    "The supportedTrust field is OPTIONAL. If absent or empty, this ERC is used only "
    "for discovery, not for trust."
)

DEFAULT_MIRROR = Path("/home/hacker/mindX/mindx/godel/mindxtrain/personas/savante.persona")

# The fifteen doctrine pointers, in the fixed order of spec §3.2. Order is load-bearing.
DOCTRINE_POINTERS: List[str] = [
    "/persona",
    "/name",
    "/source",
    "/format",
    "/system_prompt",
    "/mantra",
    "/oath",
    "/bdi/beliefs",
    "/skills/primary",
    "/skills/taxonomy",
    "/skills/defer_triggers",
    "/skills/validation",
    "/safety",
    "/embodiment",
    "/token/intelligence/tool_allowlist",
]

# The intelligence bundle — component name → repo-relative path.
COMPONENTS: List[Tuple[str, str]] = [
    ("identity", "savante.persona"),
    ("charter", ".claude/agents/savante.md"),
    ("skill", ".claude/skills/sagi/SKILL.md"),
    ("facet_agent", "sAGI.agent"),
    ("facet_model", "sAGI.model"),
    ("facet_prompt", "sAGI.prompt"),
    ("facet_tool", "sAGI.tool"),
    ("facet_voaice", "sAGI.voaice"),
    ("facet_faice", "sAGI.faice"),
]

# Ledger component name → facet extension. `charter` is deliberately absent: it is the SOURCE of the
# derived .prompt facet, not a facet of the bundle (sagi/engine/FACET_BUNDLE.md §5).
COMPONENT_FACET: Dict[str, str] = {
    "identity": "persona",
    "facet_agent": "agent",
    "facet_model": "model",
    "facet_prompt": "prompt",
    "facet_tool": "tool",
    "skill": "skill",
    "facet_voaice": "voaice",
    "facet_faice": "faice",
}

# Registry order (sagi/engine/facet_registry.json). ORDER IS LOAD-BEARING: it fixes the bundle_root
# preimage and the Merkle leaf indices. Never reorder; only append.
FACET_ORDER: List[str] = ["persona", "agent", "model", "prompt", "tool", "skill", "voaice", "faice"]

# Core facets this bundle does not author, recorded as absent WITH a reason rather than stubbed.
FACETS_ABSENT: List[Tuple[str, str]] = [
    ("attribute", "no attribute facet is authored; the office's attributes live in the persona's bdi/skills blocks"),
    ("reputation", "no reputation facet is authored; the verdict ledger has zero entries, so there is nothing earned to record"),
]

MERKLE_LEAVES = 64          # THOTCommitmentRegistry.issueTHOT4096 documents a 64-leaf tree

CARD_NAME = "savante.agentcard.json"
LEDGER_NAME = "savante.commitments.json"
MANIFEST_NAME = "savante.thot.json"

ONCHAIN_METADATA_KEYS = ["savantePersonaDigest", "savanteDoctrineRoot"]

# public_metadata keys that form the EIP-721 / ERC-8004 union, in card order.
UNION_KEYS = [
    "type", "name", "description", "image", "external_url", "animation_url",
    "background_color", "attributes", "services", "x402Support", "active",
    "registrations", "supportedTrust",
]
# Sibling annotation keys the persona author may use to carry a reason or note beside a union key
# (e.g. image_reason, services_note). They are moved into the card's `savante` object.
ANNOTATION_KEYS = {f"{k}_{suffix}" for k in UNION_KEYS for suffix in ("reason", "note")}

EXIT_OK, EXIT_GENERIC, EXIT_PREFLIGHT, EXIT_MIRROR, EXIT_POINTER, EXIT_CARD, EXIT_KECCAK = 0, 1, 2, 3, 4, 5, 6


def fail(msg: str, code: int = EXIT_GENERIC) -> None:
    sys.stderr.write(f"savante_bind: ERROR: {msg}\n")
    sys.exit(code)


# ── keccak256 ─────────────────────────────────────────────────────────────────

def load_keccak() -> Tuple[Optional[Callable[[bytes], bytes]], Optional[str]]:
    try:
        from Crypto.Hash import keccak as _keccak  # pycryptodome

        def _k(data: bytes) -> bytes:
            h = _keccak.new(digest_bits=256)
            h.update(data)
            return h.digest()

        return _k, "pycryptodome Crypto.Hash.keccak(digest_bits=256)"
    except ImportError:
        pass
    try:
        from eth_utils import keccak as _ek

        return (lambda data: bytes(_ek(data))), "eth_utils.keccak"
    except ImportError:
        pass
    return None, None


KECCAK, KECCAK_BACKEND = load_keccak()


def keccak256(data: bytes) -> bytes:
    if KECCAK is None:
        fail("no keccak256 backend: install pycryptodome or eth_utils", EXIT_KECCAK)
    return KECCAK(data)


def keccak_selftest() -> None:
    if KECCAK is None:
        fail("no keccak256 backend: install pycryptodome or eth_utils", EXIT_KECCAK)
    got = keccak256(b"").hex()
    if got != KECCAK_EMPTY_HEX:
        fail(f"keccak256 self-test failed: keccak256(b'') = {got}, expected {KECCAK_EMPTY_HEX}; "
             f"backend {KECCAK_BACKEND} is not keccak", EXIT_KECCAK)


# ── CIDv1 — reproduced VERBATIM from inft_publish.py:34-36 and :39-47 ─────────

def _b32_lower(data: bytes) -> str:
    import base64
    return base64.b32encode(data).decode("ascii").lower().rstrip("=")


def cid_v1_raw(data: bytes) -> str:
    """CIDv1 · codec raw (0x55) · multihash sha2-256 (0x12, 32 bytes) · multibase base32 ('b').
    For a blob ≤ 256 KiB this equals `ipfs add --cid-version 1 --raw-leaves` — a THOT is a
    few KB, so the name here is the name IPFS would give it. Larger artifacts are NOT
    named this way (their IPFS CID depends on chunking); they are referenced by sha256."""
    digest = hashlib.sha256(data).digest()
    multihash = bytes([0x12, 0x20]) + digest
    cid_bytes = bytes([0x01, 0x55]) + multihash
    return "b" + _b32_lower(cid_bytes)


# ── end verbatim ──────────────────────────────────────────────────────────────

def cid_or_none(data: bytes) -> Tuple[Optional[str], Optional[str]]:
    """CID for blobs <= 256 KiB; (None, reason) otherwise. Never guess a chunked CID."""
    if len(data) > CID_MAX_BYTES:
        return None, (f"{len(data)} bytes exceeds the {CID_MAX_BYTES}-byte single-block bound "
                      f"(inft_publish.py:40-43); the IPFS CID depends on chunking and cannot be "
                      f"derived locally — referenced by sha256 only")
    return cid_v1_raw(data), None


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5_hex(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


# ── RFC 6901 ──────────────────────────────────────────────────────────────────

class PointerMissing(Exception):
    pass


def escape_token(tok: str) -> str:
    return tok.replace("~", "~0").replace("/", "~1")


def unescape_token(tok: str) -> str:
    return tok.replace("~1", "/").replace("~0", "~")


def resolve(doc: Any, pointer: str) -> Any:
    """RFC 6901 JSON Pointer resolution. Raises PointerMissing on any absent step."""
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise PointerMissing(f"{pointer!r} is not an RFC 6901 pointer (must start with '/')")
    cur = doc
    for raw in pointer[1:].split("/"):
        tok = unescape_token(raw)
        if isinstance(cur, dict):
            if tok not in cur:
                raise PointerMissing(f"{pointer}: object has no member {tok!r}")
            cur = cur[tok]
        elif isinstance(cur, list):
            if not tok.isdigit():
                raise PointerMissing(f"{pointer}: {tok!r} is not an array index")
            i = int(tok)
            if i >= len(cur):
                raise PointerMissing(f"{pointer}: index {i} out of range ({len(cur)} items)")
            cur = cur[i]
        else:
            raise PointerMissing(f"{pointer}: cannot descend into a scalar at {tok!r}")
    return cur


# ── PREFLIGHT (P1 + P2) ───────────────────────────────────────────────────────

def preflight(doc: Any) -> Dict[str, Any]:
    """Walk the whole document. Returns a report; `ok` is False with `errors` naming each
    offending RFC 6901 pointer and the reason. bool is not a JSON number and is skipped."""
    names: List[str] = []
    numbers: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    def walk(v: Any, ptr: str) -> None:
        if isinstance(v, dict):
            for k, x in v.items():
                names.append(k)
                if not k.isascii():
                    errors.append({"pointer": ptr + "/" + escape_token(k), "rule": "P1",
                                   "reason": "property name is not ASCII; Python's code-point key "
                                             "sort no longer equals JCS's UTF-16 code-unit sort"})
                walk(x, ptr + "/" + escape_token(k))
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{ptr}/{i}")
        elif isinstance(v, bool) or v is None or isinstance(v, str):
            return
        elif isinstance(v, int):
            numbers.append({"pointer": ptr, "value": v})
            if abs(v) > INT_SAFE_BOUND:
                errors.append({"pointer": ptr, "rule": "P2",
                               "reason": f"integer {v} exceeds 2^53; ECMAScript number serialization "
                                         f"would differ from Python's"})
        elif isinstance(v, float):
            numbers.append({"pointer": ptr, "value": v})
            errors.append({"pointer": ptr, "rule": "P2",
                           "reason": f"number {v!r} is not an integer; json.dumps and JCS serialize "
                                     f"non-integers differently"})
        else:
            errors.append({"pointer": ptr, "rule": "P0",
                           "reason": f"non-JSON value of type {type(v).__name__}"})

    walk(doc, "")
    return {
        "ok": not errors,
        "property_name_count": len(names),
        "all_property_names_ascii": all(n.isascii() for n in names),
        "numbers": numbers,
        "errors": errors,
    }


def require_preflight(doc: Any, what: str) -> Dict[str, Any]:
    rep = preflight(doc)
    if not rep["ok"]:
        for e in rep["errors"]:
            sys.stderr.write(f"savante_bind: PREFLIGHT {e['rule']} failed in {what} at {e['pointer']}: "
                             f"{e['reason']}\n")
        fail(f"preflight failed on {what}; refusing to emit any digest", EXIT_PREFLIGHT)
    return rep


def canonical_bytes(v: Any) -> bytes:
    """Equals RFC 8785 (JCS) output ONLY under P1+P2 — callers must have run the preflight."""
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


# ── the doctrine root ─────────────────────────────────────────────────────────

CONSTRUCTION_TEXT = (
    "preimage = concat over DOCTRINE_POINTERS in the fixed order of: "
    "pointer.encode('utf-8') + b'\\x1f' + canonical_bytes(resolve(doc, pointer)) + b'\\x1e'; "
    "doctrine_root = keccak256(preimage). canonical_bytes(v) = json.dumps(v, sort_keys=True, "
    "separators=(',',':'), ensure_ascii=False).encode('utf-8'), valid only under preflight P1+P2. "
    "A missing pointer is a hard error, never a skipped term."
)


def doctrine_root(doc: Any) -> Dict[str, Any]:
    clauses = []
    preimage = b""
    for p in DOCTRINE_POINTERS:
        try:
            v = resolve(doc, p)
        except PointerMissing as e:
            fail(f"doctrine pointer missing — {e}", EXIT_POINTER)
        cb = canonical_bytes(v)
        preimage += p.encode("utf-8") + b"\x1f" + cb + b"\x1e"
        clauses.append({"pointer": p, "canonical_bytes": len(cb), "canonical_sha256": sha256_hex(cb)})
    root = keccak256(preimage)
    return {"root_hex": "0x" + root.hex(), "preimage_bytes": len(preimage), "clauses": clauses}


# ── git provenance (no wall clock) ────────────────────────────────────────────

def git(repo: Path, *args: str, raw: bool = False) -> Optional[str]:
    """raw=True keeps leading whitespace — `git status --porcelain` lines begin with a status column."""
    try:
        out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
        return out.stdout.rstrip("\n") if raw else out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_provenance(repo: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Returns (chartered, generated_from). Every value read from git or explicit null."""
    first = git(repo, "log", "--reverse", "--format=%H %cI")
    head = git(repo, "rev-parse", "HEAD")
    head_date = git(repo, "show", "-s", "--format=%cI", "HEAD") if head else None
    if first:
        first_hash, first_date = first.splitlines()[0].split(" ", 1)
        chartered = {
            "date": first_date[:10],
            "commit": first_hash,
            "commit_date": first_date,
            "source": "git log --reverse --format=%cI, first commit of this repository",
        }
    else:
        chartered = {"date": None, "commit": None, "commit_date": None,
                     "source": None, "reason": "no git history readable at the repo root"}
    uncommitted: List[str] = []
    if head:
        status = git(repo, "status", "--porcelain", "--", *[rel for _, rel in COMPONENTS], raw=True) or ""
        uncommitted = sorted(line[3:] for line in status.splitlines() if len(line) > 3)
    generated_from = {
        "repo_head_commit": head,
        "repo_head_commit_date": head_date,
        "components_differing_from_head": uncommitted,
        "note": ("no wall-clock timestamp by design — re-running over unchanged inputs must "
                 "reproduce these files byte for byte; the digests above are over the WORKING TREE, "
                 "so a non-empty components_differing_from_head means they are not the digests of "
                 "the commit named here"),
        "binder": "bind/savante_bind.py",
        "keccak_backend": KECCAK_BACKEND,
    }
    if head is None:
        generated_from["reason"] = "git HEAD unreadable at the repo root"
    return chartered, generated_from


# ── card construction ─────────────────────────────────────────────────────────

def _nullable(pm: Dict[str, Any], key: str, must_be_null: bool, default_reason: str) -> Tuple[None, str]:
    """A slot that must be null in the card. Accepts null (+ optional <key>_reason sibling) or
    {"value": null, "reason": ...}. Any non-null value is a hard error — nothing is pinned."""
    v = pm.get(key)
    reason = pm.get(f"{key}_reason")
    if isinstance(v, dict) and v.get("value", None) is None and "reason" in v:
        reason = v["reason"]
        v = None
    if v is not None:
        fail(f"public_metadata.{key} is {v!r}; it must be null at v0 — {default_reason}", EXIT_CARD)
    return None, (reason if isinstance(reason, str) and reason else default_reason)


def build_card(persona: Dict[str, Any], chartered: Dict[str, Any], generated_from: Dict[str, Any],
               digests: Dict[str, Any], root: Dict[str, Any], image_candidate: Optional[Dict[str, Any]],
               findings: List[str]) -> Dict[str, Any]:
    token = persona.get("token")
    if not isinstance(token, dict):
        fail("savante.persona has no top-level `token` object (spec §2.5); nothing to derive the card from", EXIT_CARD)
    pm = token.get("public_metadata")
    if not isinstance(pm, dict):
        fail("token.public_metadata missing or not an object", EXIT_CARD)

    unknown = sorted(k for k in pm if k not in UNION_KEYS and k not in ANNOTATION_KEYS and k != "savante")
    if unknown:
        fail(f"token.public_metadata has keys outside the EIP-721/ERC-8004 union: {unknown}; "
             f"Savante-specific content belongs under public_metadata.savante", EXIT_CARD)
    missing = [k for k in ("type", "name", "description", "services", "x402Support", "active",
                           "registrations", "supportedTrust") if k not in pm]
    if missing:
        fail(f"token.public_metadata lacks required ERC-8004 registration-v1 keys: {missing}", EXIT_CARD)

    if pm["type"] != ERC8004_TYPE:
        fail(f"public_metadata.type must be the literal {ERC8004_TYPE!r}; got {pm['type']!r}", EXIT_CARD)
    if not isinstance(pm["name"], str) or not pm["name"]:
        fail("public_metadata.name must be a non-empty string", EXIT_CARD)
    if not isinstance(pm["description"], str) or not pm["description"]:
        fail("public_metadata.description must be a non-empty string", EXIT_CARD)
    if not isinstance(pm.get("external_url", ""), str):
        fail("public_metadata.external_url must be a string", EXIT_CARD)

    image, image_reason = _nullable(pm, "image", True,
                                    "no artwork is confirmed and no CID can be derived locally for a "
                                    "file over 256 KiB (inft_publish.py:40-43); never synthesise an ipfs:// URI")
    animation, animation_reason = _nullable(pm, "animation_url", True, "no animation exists; nothing is pinned")
    bg, bg_reason = _nullable(pm, "background_color", True, "no colour is specified; the card asserts nothing it does not have")

    attributes = pm.get("attributes", [])
    if not isinstance(attributes, list):
        fail("public_metadata.attributes must be a list", EXIT_CARD)
    out_attrs: List[Dict[str, Any]] = []
    for i, a in enumerate(attributes):
        if not isinstance(a, dict) or "trait_type" not in a or "value" not in a:
            fail(f"public_metadata.attributes[{i}] must be {{trait_type, value}}", EXIT_CARD)
        extra = sorted(k for k in a if k not in ("trait_type", "value", "display_type"))
        if extra:
            fail(f"public_metadata.attributes[{i}] has unexpected keys {extra}", EXIT_CARD)
        if "display_type" in a and not (isinstance(a["value"], int) and not isinstance(a["value"], bool)):
            fail(f"public_metadata.attributes[{i}]: display_type is allowed only on integer counts", EXIT_CARD)
        if not isinstance(a["value"], (str, int)) or isinstance(a["value"], bool):
            fail(f"public_metadata.attributes[{i}].value must be a string or an integer", EXIT_CARD)
        entry: Dict[str, Any] = {"trait_type": a["trait_type"], "value": a["value"]}
        if "display_type" in a:
            entry["display_type"] = a["display_type"]
        out_attrs.append(entry)
    # The chartered date is derived from git, never a literal. A literal that disagrees is an error.
    existing = [a for a in out_attrs if str(a["trait_type"]).lower() == "chartered"]
    if existing:
        if chartered["date"] is None:
            fail("attributes carry a 'Chartered' literal but git history is unreadable; cannot verify it", EXIT_CARD)
        if existing[0]["value"] != chartered["date"]:
            fail(f"attributes 'chartered' = {existing[0]['value']!r} disagrees with the first commit date "
                 f"{chartered['date']!r} ({chartered['commit']})", EXIT_CARD)
    elif chartered["date"] is not None:
        out_attrs.append({"trait_type": "chartered", "value": chartered["date"]})
    else:
        findings.append("chartered date not derivable: git history unreadable; no 'chartered' attribute written")

    services = pm["services"]
    if not (isinstance(services, list) and len(services) == 1 and isinstance(services[0], dict)
            and services[0].get("name") == "web" and isinstance(services[0].get("endpoint"), str)):
        fail("public_metadata.services must be exactly one entry {name:'web', endpoint:<url>} at v0 "
             "(spec §4) — no other endpoint exists to advertise", EXIT_CARD)
    if pm["x402Support"] is not False:
        fail("public_metadata.x402Support must be false — no x402 endpoint exists", EXIT_CARD)
    if pm["active"] is not True:
        fail("public_metadata.active must be true", EXIT_CARD)
    if pm["registrations"] != []:
        fail("public_metadata.registrations must be [] at v0: nothing is minted and token.bindings is null", EXIT_CARD)
    if pm["supportedTrust"] != []:
        fail("public_metadata.supportedTrust must be [] — no trust model is demonstrated", EXIT_CARD)

    pm_sav = pm.get("savante", {})
    if not isinstance(pm_sav, dict):
        fail("public_metadata.savante must be an object", EXIT_CARD)
    proposed = pm_sav.get("proposed_services")
    if not isinstance(proposed, list) or not proposed:
        fail("public_metadata.savante.proposed_services must be a non-empty list", EXIT_CARD)
    for i, s in enumerate(proposed):
        if not isinstance(s, dict) or not {"mode", "status", "deciding_experiment"} <= set(s):
            fail(f"proposed_services[{i}] must carry mode, status, deciding_experiment", EXIT_CARD)
        if s["status"] != "not_yet_deployed":
            fail(f"proposed_services[{i}].status is {s['status']!r}; only 'not_yet_deployed' may be "
                 f"asserted — a field that asserts reachability is not where an aspiration goes", EXIT_CARD)

    status = token.get("status")
    if status not in ("not_yet_minted", "dry_run", "minted"):
        fail(f"token.status {status!r} outside the closed vocabulary not_yet_minted|dry_run|minted", EXIT_CARD)
    if status != "not_yet_minted":
        fail(f"token.status is {status!r} but token.bindings are null by rule and this binder has no "
             f"network; the only status it can attest is not_yet_minted", EXIT_CARD)

    savante_obj: Dict[str, Any] = {
        "derived_output": ("written by bind/savante_bind.py from savante.persona token.public_metadata; "
                           "regenerable; never hand-edited"),
        "status": status,
        "status_note": token.get("status_note"),
        "chartered": chartered,
        "image_reason": image_reason,
        "animation_url_reason": animation_reason,
        "background_color_reason": bg_reason,
        "attributes_note": pm.get("attributes_note") or (
            "display_type is an OpenSea de-facto convention, non-normative in EIP-721 and ERC-8004; "
            "it appears only on integer counts"),
        "registrations_note": pm.get("registrations_note") or (
            f"empty at v0 — nothing is minted. ERC-8004 ({ERC8004_STATUS}): \"{ERC8004_REGISTRATIONS_QUOTE}\""),
        "supportedTrust_note": pm.get("supportedTrust_note") or (
            f"empty — ERC-8004 ({ERC8004_STATUS}): \"{ERC8004_SUPPORTEDTRUST_QUOTE}\" That is precisely true today."),
        "proposed_services": proposed,
        "integrity": {
            "ledger": LEDGER_NAME,
            "onchain_metadata_keys": ONCHAIN_METADATA_KEYS,
            "doctrine_pointers": DOCTRINE_POINTERS,
            "doctrine_root": root["root_hex"],
            "persona_sha256": digests["identity"]["sha256"],
            "charter_sha256": digests["charter"]["sha256"],
            "skill_sha256": digests["skill"]["sha256"],
            "note": ("recompute with `python3 bind/savante_verify.py .`; the card's own CID lives only in "
                     "the ledger because a document cannot carry its own digest"),
        },
        "image_candidate": image_candidate,
        # The git HEAD and working-tree state live in the LEDGER only. A card that
        # named the commit it lives in could never be consistent with any commit:
        # the card naming X exists only after X, and committing it makes Y.
        "provenance": {"ledger": LEDGER_NAME,
                       "note": "repo_head_commit and components_differing_from_head are recorded in the ledger, never here"},
    }
    # Persona-authored annotations win over binder defaults; unknown notes are carried, not dropped.
    for k in sorted(ANNOTATION_KEYS & set(pm)):
        if isinstance(pm[k], str) and pm[k]:
            savante_obj[k] = pm[k]
    for k, v in pm_sav.items():
        if k not in savante_obj:
            savante_obj[k] = v

    card: Dict[str, Any] = {
        "$comment": ("DERIVED OUTPUT — generated by bind/savante_bind.py from savante.persona; regenerable; "
                     "never hand-edited. EIP-721 metadata (name, description, image) and ERC-8004 "
                     "registration-v1 in one document; everything Savante-specific is under `savante`."),
        "type": pm["type"],
        "name": pm["name"],
        "description": pm["description"],
        "image": image,
        "external_url": pm.get("external_url"),
        "animation_url": animation,
        "background_color": bg,
        "attributes": out_attrs,
        "services": services,
        "x402Support": False,
        "active": True,
        "registrations": [],
        "supportedTrust": [],
        "savante": savante_obj,
    }
    return card


# ── serialisation ─────────────────────────────────────────────────────────────

def dump_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def digest_file(path: Path) -> Dict[str, Any]:
    data = path.read_bytes()
    cid, reason = cid_or_none(data)
    d: Dict[str, Any] = {"bytes": len(data), "sha256": sha256_hex(data), "cid": cid}
    if reason:
        d["cid_reason"] = reason
    return d


# ── the facet bundle ──────────────────────────────────────────────────────────
# sagi/engine/FACET_BUNDLE.md (what the facets are) and THOT_MANIFEST.md (how they become one
# content-addressed thing). Every check here FAILS CLOSED: a derived facet that has drifted is not a
# warning, because the whole point of deriving it was that it cannot drift silently.

US, RS = b"\x1f", b"\x1e"


def frontmatter_body(text: str, what: str) -> str:
    """Everything after the closing '---' of the YAML frontmatter."""
    if not text.startswith("---\n"):
        fail(f"{what}: no YAML frontmatter (expected a leading '---' line)", EXIT_POINTER)
    try:
        return text[text.index("\n---\n", 3) + len("\n---\n"):]
    except ValueError:
        fail(f"{what}: frontmatter is never closed (no second '---' line)", EXIT_POINTER)
        raise  # unreachable; fail() exits


def frontmatter_tools(text: str, what: str) -> List[str]:
    """The `tools:` allowlist from a charter's frontmatter, in declared order."""
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        if line.startswith("tools:"):
            return [t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()]
    fail(f"{what}: frontmatter has no `tools:` line", EXIT_POINTER)
    raise  # unreachable


def check_prompt_derivation(repo: Path) -> Dict[str, Any]:
    """sAGI.prompt's body must equal the charter body BYTE FOR BYTE. Fail closed on drift.

    The error names the offending byte offset and the regeneration command, because a fail-closed
    gate that only says 'mismatch' reads as a broken build to whoever meets it first."""
    charter_rel, prompt_rel = ".claude/agents/savante.md", "sAGI.prompt"
    charter_text = (repo / charter_rel).read_text(encoding="utf-8")
    prompt_text = (repo / prompt_rel).read_text(encoding="utf-8")
    want = frontmatter_body(charter_text, charter_rel)
    got = frontmatter_body(prompt_text, prompt_rel)
    if want != got:
        off = next((i for i, (a, b) in enumerate(zip(want, got)) if a != b), min(len(want), len(got)))
        fail(
            f"{prompt_rel} has DRIFTED from {charter_rel}: bodies differ at byte offset {off} of the body "
            f"(charter body {len(want)} B, prompt body {len(got)} B).\n"
            f"  charter: {want[off:off + 60]!r}\n"
            f"  prompt : {got[off:off + 60]!r}\n"
            f"  The charter is authoritative (technical.md:16-18). Regenerate, never hand-edit:\n"
            f"    python3 - <<'PY'\n"
            f"    c = open('{charter_rel}').read(); p = open('{prompt_rel}').read()\n"
            f"    i = c.index(chr(10)+'---'+chr(10), 3) + 5; j = p.index(chr(10)+'---'+chr(10), 3) + 5\n"
            f"    open('{prompt_rel}', 'w').write(p[:j] + c[i:])\n"
            f"    PY",
            EXIT_POINTER,
        )
    return {"source": charter_rel, "derivation": "body after the closing frontmatter delimiter, byte-for-byte",
            "body_bytes": len(want.encode("utf-8")), "equal": True}


def check_tool_facet(repo: Path, persona: Dict[str, Any]) -> Dict[str, Any]:
    """The allowlist must agree in all THREE places, or the bundle is lying somewhere."""
    charter_text = (repo / ".claude/agents/savante.md").read_text(encoding="utf-8")
    from_charter = frontmatter_tools(charter_text, ".claude/agents/savante.md")
    from_persona = resolve(persona, "/token/intelligence/tool_allowlist")
    tool = json.loads((repo / "sAGI.tool").read_text(encoding="utf-8"))
    from_facet = [row["tool"] for row in tool.get("allowlist", [])]

    if from_charter != from_persona:
        fail(f"tool allowlist disagrees: charter {from_charter} != persona {from_persona}", EXIT_POINTER)
    if from_charter != from_facet:
        fail(f"tool allowlist disagrees: charter {from_charter} != sAGI.tool {from_facet}", EXIT_POINTER)

    legal = {"harness", "nothing", "executor_that_does_not_exist"}
    rows = list(tool.get("allowlist", [])) + list(tool.get("forbidden_tools", [])) \
        + list(tool.get("grants", {}).get("mask", [])) + list(tool.get("grants", {}).get("forbidden", []))
    for row in rows:
        if row.get("enforced_by") not in legal:
            fail(f"sAGI.tool row {row!r} has enforced_by={row.get('enforced_by')!r}; legal values are {sorted(legal)}. "
                 "A capability surface that does not say what enforces it is worse than none.", EXIT_POINTER)
    return {"allowlist": from_charter, "agrees": ["charter frontmatter", "persona /token/intelligence/tool_allowlist",
                                                  "sAGI.tool allowlist[]"], "rows_checked": len(rows)}


def check_embodiment_facet(repo: Path, rel: str, fmt: str, print_key: str) -> Dict[str, Any]:
    """voaice/faice: the honest-null rule. A measured print without measurements, or a null print
    without a reason, are both defects — the first claims, the second hides."""
    doc = json.loads((repo / rel).read_text(encoding="utf-8"))
    if doc.get("format") != fmt:
        fail(f"{rel}: format is {doc.get('format')!r}, expected {fmt!r}", EXIT_POINTER)
    measured, printed = doc.get("measured"), doc.get(print_key)
    if (measured is None) != (printed is None):
        fail(f"{rel}: measured and {print_key} must be null together or present together "
             f"(measured={'null' if measured is None else 'present'}, "
             f"{print_key}={'null' if printed is None else 'present'})", EXIT_POINTER)
    state = "null_with_reason" if measured is None else "present"
    if measured is None:
        prov = doc.get("provenance") or {}
        if not prov.get("reason") or not prov.get("deciding_experiment"):
            fail(f"{rel}: unmeasured, so provenance.reason AND provenance.deciding_experiment are required. "
                 "A null without a reason is a hole; a null with one is a finding.", EXIT_POINTER)
    return {"format": fmt, "state": state, "measured": measured is not None}


def merkle_root(leaves: List[bytes]) -> str:
    """Pairwise keccak256 over exactly MERKLE_LEAVES leaves, padded with keccak256(b'') (THOT_MANIFEST.md §5).

    More than MERKLE_LEAVES leaves is an error, never a truncation: a root over the first 64 would commit
    to less than the bundle and still look like a root over all of it."""
    if len(leaves) > MERKLE_LEAVES:
        raise ValueError(f"{len(leaves)} leaves exceed the {MERKLE_LEAVES}-leaf tree; "
                         "THOT_MANIFEST.md §5 fails rather than truncates")
    pad = keccak256(b"")
    level = list(leaves) + [pad] * (MERKLE_LEAVES - len(leaves))
    while len(level) > 1:
        level = [keccak256(level[i] + level[i + 1]) for i in range(0, len(level), 2)]
    return "0x" + level[0].hex()


# ── hash agility: the closed algorithm vocabulary (sagi/engine/THOT_MANIFEST.md §3a) ─────────────────
# sagi.thot_manifest/1 knows exactly these ten keys (plus the free-text `note`), each with exactly one
# value, compared as exact strings after JSON decoding. The binder emits them; the verifier REFUSES a
# missing block, a missing required key, an unknown key, or any other value. ui.py carries a literal copy
# (it depends on nothing but gradio) and `savante_verify.py --self-test` fails if the two drift.
CANONICALISATION = "json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')"
ALGORITHMS_ALWAYS: Dict[str, str] = {
    "facet_digest": "sha256",
    "cid": "cidv1-raw-sha2-256-base32",
    "bundle_root": "keccak256",
    "merkle_leaf": "keccak256",
    "merkle_pad": "keccak256",
    "identity_thot": "sha256",
    "identity_content_root": "keccak256",
    "canonicalisation": CANONICALISATION,
}
ALGORITHMS_CONDITIONAL: Dict[str, str] = {
    # required iff the manifest carries a non-null top-level `doctrine_root`
    "doctrine_root": "keccak256",
    # required iff condition G holds (git_blob_condition below; Savante's manifest does not trigger it)
    "git_blob": "sha1 over b'blob <len>\\x00' + bytes (git's own object id; used only to name the referenced voice)",
}
ALGORITHMS_RESERVED = ("note",)


def manifest_algorithms() -> Dict[str, str]:
    """The block this binder emits: every always-key, plus doctrine_root because Savante has one."""
    a = {k: ALGORITHMS_ALWAYS[k] for k in ("facet_digest", "cid", "bundle_root", "merkle_leaf", "merkle_pad")}
    a["doctrine_root"] = ALGORITHMS_CONDITIONAL["doctrine_root"]
    a.update({k: ALGORITHMS_ALWAYS[k] for k in ("identity_thot", "identity_content_root", "canonicalisation")})
    a["note"] = ("A verifier MUST refuse a manifest whose algorithms block is missing, lacks a required key, "
                 "carries a key outside the sagi.thot_manifest/1 vocabulary, or declares a value it does not "
                 "implement (sagi/engine/THOT_MANIFEST.md §3a), rather than verify with the functions it "
                 "happens to have. Silently checking the wrong digest is worse than not checking.")
    return a


SCHEMA = "sagi.thot_manifest/1"
GIT_BLOB_KEY_PREFIX = "git_blob"     # §3a condition G: a case-sensitive key PREFIX, never a substring


class DuplicateKey(ValueError):
    """A JSON object names the same key twice. json.loads would keep the last value silently, so the bytes a
    third-party parser reads could declare something other than what this program checked."""


def _no_duplicates(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in pairs:
        if k in out:
            raise DuplicateKey(f"duplicate key {k!r} in one JSON object")
        out[k] = v
    return out


def loads_strict(text: str) -> Any:
    """json.loads that refuses duplicate keys anywhere in the document (raises DuplicateKey, a ValueError)."""
    return json.loads(text, object_pairs_hook=_no_duplicates)


def git_blob_condition(manifest: Any) -> bool:
    """§3a condition G, exactly as written — the ONE definition; savante_verify.py and ui.py import it.

    Walk each element of the top-level `facets` and `custom` arrays (a missing or non-array value counts as
    empty), through objects and arrays at any depth, the element included. G holds iff some object KEY
    satisfies key.startswith("git_blob"), case-sensitive. Key values are never inspected (a null value still
    triggers), string values are never tested, and nothing outside facets[]/custom[] is walked (not absent[],
    relations[], references[], rung or algorithms). A verifier MUST NOT widen G: commit ids, 40-hex or 64-hex
    values, and keys such as git_object / oid / sha1 / commit never trigger it. Savante names none: False."""
    def walk(v: Any) -> bool:
        if isinstance(v, dict):
            return any((isinstance(k, str) and k.startswith(GIT_BLOB_KEY_PREFIX)) or walk(x) for k, x in v.items())
        if isinstance(v, list):
            return any(walk(x) for x in v)
        return False
    if not isinstance(manifest, dict):
        return False
    return any(walk(e) for k in ("facets", "custom") if isinstance(manifest.get(k), list) for e in manifest[k])


def algorithms_refusals(manifest: Any) -> List[str]:
    """Every reason §3a rule 1 refuses this manifest; empty means the declaration is exactly what this
    program implements. Runs before any digest (§8 step 0)."""
    schema = manifest.get("schema") if isinstance(manifest, dict) else None
    out: List[str] = [] if schema == SCHEMA else [
        f"schema = {schema!r}; this verifier implements only {SCHEMA!r}, and a successor vocabulary is a new "
        "schema version (§3a) — its algorithms are not checked against the /1 table"]
    algs = manifest.get("algorithms") if isinstance(manifest, dict) else None
    if not isinstance(algs, dict):
        return out + ["the `algorithms` block is missing or is not a JSON object (§3a rule 1a) — an absent "
                      "declaration is an assumption, and a digest checked under an assumption is not a check"]
    if "note" in algs and not isinstance(algs["note"], str):
        out.append(f"algorithms.note is a {type(algs['note']).__name__}, not a string; `note` is reserved "
                   "for free text (§3a)")
    required = dict(ALGORITHMS_ALWAYS)
    if manifest.get("doctrine_root") is not None:
        required["doctrine_root"] = ALGORITHMS_CONDITIONAL["doctrine_root"]
    if git_blob_condition(manifest):
        required["git_blob"] = ALGORITHMS_CONDITIONAL["git_blob"]
    out += [f"algorithms.{k} is missing; this verifier requires {v!r} (§3a rule 1b)"
            for k, v in required.items() if k not in algs]
    known = {**ALGORITHMS_ALWAYS, **ALGORITHMS_CONDITIONAL}
    for k, v in algs.items():
        if k in ALGORITHMS_RESERVED:
            continue
        if k not in known:
            out.append(f"algorithms.{k} is not a sagi.thot_manifest/1 key (§3a rule 1c)")
        elif v != known[k]:
            out.append(f"algorithms.{k} = {v!r}; this verifier implements {known[k]!r} (§3a rule 1d)")
    return out


# ── lineage: generations (sagi/engine/THOT_MANIFEST.md §7) ────────────────────────────────────────────
# P is the most recent manifest of this bundle. The binder reads it from LOCAL git only (`git show
# <rev>:savante.thot.json`; no fetch, no network) and takes `bundle.parent` from P's own `identity.cid`,
# after checking that P's file reproduces that CID — never from a local re-bind.
BUNDLE_ID = "sAGI"
CID_RE = re.compile(r"^bafkrei[a-z2-7]{52}$")
LOCATOR_RE = re.compile(r"^[^/@\s]+/[^/@\s]+/[^/@\s]+@[0-9a-f]{40}$")
GENESIS_REASON = "genesis generation; there is no earlier manifest"


def git_bytes(repo: Path, rev: str, rel: str) -> Optional[bytes]:
    """The raw bytes of `rel` in commit `rev` of the LOCAL clone, or None. Never fetches."""
    try:
        out = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{rel}"], capture_output=True, check=True)
        return out.stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def manifest_identity_cid(m: Dict[str, Any]) -> Optional[str]:
    """§2 under identity-only scope: cid_v1_raw over canonical_bytes(manifest WITHOUT its identity block)."""
    return cid_or_none(canonical_bytes({k: v for k, v in m.items() if k != "identity"}))[0]


def present_facet_digests(m: Dict[str, Any]) -> Dict[str, Any]:
    """The §7 facet-change basis: {facet label: sha256} over the present facets, custom facets included."""
    out: Dict[str, Any] = {}
    for key in ("facets", "custom"):
        arr = m.get(key)
        for e in (arr if isinstance(arr, list) else []):
            if isinstance(e, dict) and e.get("state", "present") == "present":
                out[str(e.get("facet"))] = e.get("sha256")
    return out


def successor_change(prev: Dict[str, Any], new: Dict[str, Any]) -> bool:
    """G3's other trigger: a `schema` change, or a changed value of an algorithms key both manifests declare
    (`note` excluded). Adding or removing a conditional key with its v1 value is G4, not a successor."""
    if prev.get("schema") != new.get("schema"):
        return True
    pa, na = prev.get("algorithms"), new.get("algorithms")
    if not isinstance(pa, dict) or not isinstance(na, dict):
        return True
    return any(pa[k] != na[k] for k in pa.keys() & na.keys() if k != "note")


def _is_generation(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool) and v >= 1


def decide_bundle(new: Dict[str, Any], head_prev: Optional[Dict[str, Any]], parent_p: Optional[Dict[str, Any]],
                  parent_reason: Optional[str]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """§7 G1-G5 as a pure decision: (generation/parent/parent_reason, None), or (None, the refusal).

    `new` is the manifest being built; `head_prev` the manifest committed at HEAD (None if HEAD has none);
    `parent_p` the manifest read from --parent-commit (None without the flag)."""
    if parent_p is None:
        if parent_reason is not None:
            return None, "--parent-reason is meaningful only with --parent-commit (G2)"
        if head_prev is None:
            return {"generation": 1, "parent": None, "parent_reason": GENESIS_REASON}, None            # G1
        hb = head_prev.get("bundle") if isinstance(head_prev.get("bundle"), dict) else {}
        if hb.get("id") != BUNDLE_ID:
            return None, f"HEAD's manifest is bundle {hb.get('id')!r}, not {BUNDLE_ID!r}"
        if present_facet_digests(head_prev) != present_facet_digests(new) or successor_change(head_prev, new):
            return None, ("G5: the facets (or the schema/algorithms) differ from HEAD's manifest, generation "
                          f"{hb.get('generation')}; a facet change is never bound under an unchanged generation. "
                          "Pass --parent-commit <commit whose savante.thot.json is the most recent published "
                          "manifest> and --parent-reason '<what changed>'")
        if ((head_prev.get("rung") or {}).get("value")) != "referenced":
            return None, "G4: HEAD's manifest is anchored (rung above `referenced`); an anchored manifest is never re-bound"
        if not _is_generation(hb.get("generation")) or not isinstance(hb.get("parent_reason"), str) \
                or not hb["parent_reason"] or (hb["generation"] == 1) != (hb.get("parent") is None):
            return None, "HEAD's manifest carries a malformed bundle block (V1-V4); refusing to carry it forward"
        return {"generation": hb["generation"], "parent": hb.get("parent"),                          # G4
                "parent_reason": hb["parent_reason"]}, None
    pb = parent_p.get("bundle") if isinstance(parent_p.get("bundle"), dict) else {}
    pcid = (parent_p.get("identity") or {}).get("cid") if isinstance(parent_p.get("identity"), dict) else None
    if pb.get("id") != BUNDLE_ID:
        return None, f"P is bundle {pb.get('id')!r}; a parent is never another bundle's manifest (G2)"
    if not _is_generation(pb.get("generation")):
        return None, f"P's bundle.generation {pb.get('generation')!r} is not an integer >= 1"
    if not (isinstance(pcid, str) and CID_RE.match(pcid)):
        return None, f"P's identity.cid {pcid!r} is not a bafkrei CID"
    if manifest_identity_cid(parent_p) != pcid:
        return None, "P's file does not reproduce its own identity.cid; it is not a published manifest to descend from"
    if not (isinstance(parent_reason, str) and parent_reason.strip()):
        return None, "G2: --parent-reason is required, a non-empty string saying what changed since P"
    if present_facet_digests(parent_p) == present_facet_digests(new) and not successor_change(parent_p, new):
        return None, ("G4: no facet change and no successor since P, so there is no new generation to bind; "
                      "re-bind without --parent-commit")
    if head_prev is not None and (head_prev.get("identity") or {}).get("cid") != pcid:
        hb = head_prev.get("bundle") if isinstance(head_prev.get("bundle"), dict) else {}
        if not (hb.get("generation") == pb["generation"] + 1 and hb.get("parent") == pcid):
            return None, (f"HEAD's manifest (generation {hb.get('generation')}, parent {hb.get('parent')}) is neither P "
                          "nor a generation of P, so P is not the most recent manifest of this bundle")
        if present_facet_digests(head_prev) != present_facet_digests(new) or successor_change(head_prev, new):
            return None, (f"G5: HEAD already carries generation {hb['generation']} of P and the facets differ from it; "
                          "the next facet change is a new generation with --parent-commit HEAD")
    return {"generation": pb["generation"] + 1, "parent": pcid, "parent_reason": parent_reason}, None     # G2/G3


def build_manifest(repo: Path, digests: Dict[str, Any], root: Dict[str, Any],
                   generated_from: Dict[str, Any], persona: Dict[str, Any],
                   derivations: Dict[str, Any], head_prev: Optional[Dict[str, Any]] = None,
                   parent_p: Optional[Dict[str, Any]] = None,
                   parent_reason: Optional[str] = None) -> Tuple[Dict[str, Any], bytes]:
    """N facets → one content-addressed THOT. No salt, no timestamp, no wall clock: a content root
    that is not reproducible from the repository alone is a random number, not a content root."""
    by_facet = {COMPONENT_FACET[name]: (name, d) for name, d in digests.items() if name in COMPONENT_FACET}

    # What the LOCATOR actually holds. The rung is `referenced` because a locator exists — but a
    # locator that resolves to a tree missing half the facets does not let a stranger retrieve them,
    # and a rung that implies otherwise is the same defect one layer out from a ledger hashing bytes
    # no commit contains. Measured from git, never assumed. §6: being in the locator commit's tree is not
    # enough — a facet is held only if its bytes AT that commit hash to the sha256 this manifest records.
    head = generated_from.get("repo_head_commit")

    def held(rel: str, sha: str) -> bool:
        at = git_bytes(repo, head, rel) if head else None
        return at is not None and sha256_hex(at) == sha

    facets, preimage, leaves = [], b"", []
    for ext in FACET_ORDER:
        name, d = by_facet[ext]
        facets.append({"facet": ext, "path": d["path"], "bytes": d["bytes"], "sha256": d["sha256"],
                       "cid": d["cid"], "state": "present", "custom": False, "added_in": 1,
                       "component": name, "at_locator": held(d["path"], d["sha256"])})
        piece = ext.encode("utf-8") + US + d["sha256"].encode("ascii")
        preimage += piece + RS
        leaves.append(keccak256(piece))

    if len(leaves) > MERKLE_LEAVES:
        fail(f"{len(leaves)} present facets exceed the {MERKLE_LEAVES}-leaf Merkle tree; "
             "THOT_MANIFEST.md §5 fails rather than truncates")

    manifest: Dict[str, Any] = {
        "$comment": ("DERIVED OUTPUT — generated by bind/savante_bind.py; regenerable; never hand-edited. "
                     "This file contains no digest of itself: `identity` is computed over the document WITHOUT "
                     "the identity block. Spec: sagi/engine/THOT_MANIFEST.md."),
        "schema": "sagi.thot_manifest/1",
        # HASH AGILITY. The algorithms are DATA, not assumptions baked into a reader. A manifest is
        # immutable once anchored, and a 200-year format whose digests are all sha256/keccak256 with
        # no in-band way to name a successor dies entirely on the day either one falls. Declaring them
        # costs nothing now and is impossible to add later. Migration rule in THOT_MANIFEST.md: a new
        # generation names the successor algorithm and carries the old manifest's CID as `parent`;
        # the superseded digests are preserved as historical evidence and never recomputed in place.
        "algorithms": manifest_algorithms(),
        # §7: filled in below by decide_bundle, once the facets it compares against P are known.
        "bundle": {"id": BUNDLE_ID, "officer": persona.get("name"), "generation": None, "parent": None,
                   "parent_reason": None},
        "facets": facets,
        "absent": [{"facet": f, "state": "absent", "reason": r} for f, r in FACETS_ABSENT],
        "custom": [],
        "custom_rule": ("an extension outside the core registry MUST match ^x-[a-z0-9]+\\.[a-z0-9_]+$ and declare "
                        "{owner, spec_url, media, added_in} here; an unnamespaced unknown extension is a hard error"),
        "charter": {"path": digests["charter"]["path"], "bytes": digests["charter"]["bytes"],
                    "sha256": digests["charter"]["sha256"], "cid": digests["charter"]["cid"],
                    "role": "SOURCE of the derived .prompt facet; binding, and not itself a facet"},
        "derivations": derivations,
        "doctrine_root": root["root_hex"],
        "doctrine_root_note": ("the officer's immutable clauses — a DIFFERENT question from bundle_root. Adding a facet "
                               "must not ring the doctrine alarm, or holders learn to ignore it."),
        "bundle_root": {
            "value": "0x" + keccak256(preimage).hex(),
            "hash": "keccak256",
            "construction": "concat over facets in registry order of (ext_utf8 + 0x1f + sha256_hex_ascii + 0x1e)",
            "preimage_bytes": len(preimage),
            "order": FACET_ORDER,
        },
        "merkle": {
            "leaves": MERKLE_LEAVES,
            "leaf_rule": "keccak256(ext_utf8 || 0x1f || sha256_hex_ascii), facets in registry order",
            "padding": "keccak256(b'') for every unused leaf — a documented constant, never a repeat of the last leaf",
            "populated": len(leaves),
            "root": merkle_root(leaves),
            "ternary_head": "persona",
            "ternary_head_index": 0,
            "why": ("THOTCommitmentRegistry.issueTHOT4096 documents `root` as a Merkle root over 64 leaves; passing a "
                    "flat digest into that slot would verify and would mean something other than what the contract says"),
        },
        "rung": {
            "value": "referenced",
            "derived_by": "permanence/lib/rungs.js rungOf(evidence) — derived from evidence, never asserted",
            "ladder": ["referenced", "committed", "stored", "attested"],
            "evidence": {
                "locator": f"github.com/cryptoAGI/savante@{generated_from.get('repo_head_commit')}",
                "locator_holds": [f["facet"] for f in facets if f["at_locator"]],
                "locator_lacks": [f["facet"] for f in facets if not f["at_locator"]],
                "commitTx": None, "dataTx": None, "attestation": None,
            },
            "note": ("nothing is uploaded and nothing is on chain; `stored` requires a data transaction "
                     "id, not an intention"),
            "locator_caveat": ("`referenced` means a locator exists — NOT that the locator holds these "
                               "bytes. Any facet in `locator_lacks` is absent from that commit's tree, so "
                               "a stranger resolving the locator cannot retrieve it. The rung stays "
                               "`referenced` because that is what the evidence supports; it becomes "
                               "honest-in-full only once `locator_lacks` is empty, which a commit fixes."),
        },
        "license": resolve(persona, "/token/rights/license"),
    }

    refusals = algorithms_refusals(manifest)
    if refusals:
        fail("the manifest this binder built would be refused by the verifier: " + "; ".join(refusals))
    if not LOCATOR_RE.match(manifest["rung"]["evidence"]["locator"]):
        fail(f"rung.evidence.locator {manifest['rung']['evidence']['locator']!r} is not "
             "<host>/<owner>/<repo>@<40 lowercase hex> (§3 S10); the locator needs a readable git HEAD")

    lineage, refusal = decide_bundle(manifest, head_prev, parent_p, parent_reason)
    if refusal:
        fail(f"lineage (THOT_MANIFEST.md §7): {refusal}")
    manifest["bundle"].update(lineage)

    canon = canonical_bytes(manifest)
    sha = sha256_hex(canon)
    cid, cid_reason = cid_or_none(canon)
    manifest["identity"] = {
        "thot": "thot:" + sha,
        "cid": cid,
        "name": ("thot-" + cid) if cid else None,
        "contentRoot": "0x" + keccak256(canon).hex(),
        "canonical_bytes": len(canon),
        "construction": ("sha256 / cid_v1_raw / keccak256 over canonical_bytes(manifest WITHOUT this identity block); "
                         "no salt, no timestamp — reproducible from the repository alone"),
    }
    if cid_reason:
        manifest["identity"]["cid_reason"] = cid_reason
    return manifest, dump_bytes(manifest)


# ── main ──────────────────────────────────────────────────────────────────────

def run_bind(repo: Path, out_dir: Path, mirror: Path, no_mirror_check: bool, image: Optional[Path],
             parent_commit: Optional[str] = None, parent_reason: Optional[str] = None,
             image_named: Optional[str] = None) -> int:
    keccak_selftest()
    findings: List[str] = []

    persona_path = repo / "savante.persona"
    for _, rel in COMPONENTS:
        if not (repo / rel).is_file():
            fail(f"component missing: {repo / rel}")
    persona_bytes = persona_path.read_bytes()
    try:
        persona = json.loads(persona_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        fail(f"savante.persona is not valid UTF-8 JSON: {e}")

    # MIRROR CHECK — fail closed.
    mirror_report: Dict[str, Any]
    if no_mirror_check:
        findings.append("MIRROR CHECK SKIPPED by --no-mirror-check: the mindX loader copy at "
                        f"{mirror} was not compared; if it differs, the ledger commits to one document "
                        "while corpus.PERSONA_DIR teaches another (spec §12.3)")
        mirror_report = {"checked": False, "path": str(mirror), "reason": "--no-mirror-check"}
    else:
        if not mirror.is_file():
            fail(f"mirror not found: {mirror} (override with --mirror, or record the skip with --no-mirror-check)", EXIT_MIRROR)
        m_repo, m_mirror = md5_hex(persona_bytes), md5_hex(mirror.read_bytes())
        if m_repo != m_mirror:
            fail(f"mirror md5 mismatch: {persona_path} = {m_repo}, {mirror} = {m_mirror}", EXIT_MIRROR)
        mirror_report = {"checked": True, "path": str(mirror), "md5": m_repo, "equal": True}

    # PREFLIGHT over the whole persona — before any digest.
    pre = require_preflight(persona, "savante.persona")

    # FACET CHECKS — before any digest, because a digest of a drifted facet is a true hash of a
    # false claim. Each of these fails closed (sagi/engine/FACET_BUNDLE.md §5-§7).
    derivations = {
        "prompt": check_prompt_derivation(repo),
        "tool": check_tool_facet(repo, persona),
        "voaice": check_embodiment_facet(repo, "sAGI.voaice", "voaice/1", "vprint"),
        "faice": check_embodiment_facet(repo, "sAGI.faice", "faice/1", "fprint"),
    }

    # token.bindings must be null values — the persona never carries mint results.
    token = persona.get("token")
    if not isinstance(token, dict):
        fail("savante.persona has no top-level `token` object (spec §2.5)", EXIT_POINTER)
    bindings = token.get("bindings")
    if not isinstance(bindings, dict):
        fail("token.bindings missing", EXIT_CARD)
    erc = bindings.get("erc8004", {})
    for k in ("agentRegistry", "agentId", "agentURI"):
        if erc.get(k) is not None:
            fail(f"token.bindings.erc8004.{k} = {erc[k]!r}; binding values are permanently null in the "
                 f"persona and live only in {LEDGER_NAME}", EXIT_CARD)
    if erc.get("metadata_keys") not in (None, ONCHAIN_METADATA_KEYS):
        fail(f"token.bindings.erc8004.metadata_keys {erc.get('metadata_keys')!r} != {ONCHAIN_METADATA_KEYS}", EXIT_CARD)
    # The persona's declared components must be exactly the components this ledger binds — no more, no fewer.
    try:
        comps = resolve(persona, "/token/intelligence/components")
    except PointerMissing as e:
        fail(f"persona component list missing — {e}", EXIT_POINTER)
    declared = [(c.get("component"), c.get("path")) for c in comps if isinstance(c, dict)] \
        if isinstance(comps, list) else []
    if not isinstance(comps, list) or len(declared) != len(comps) or len(set(declared)) != len(declared) \
            or set(declared) != set(COMPONENTS):
        fail(f"persona /token/intelligence/components {declared} != the {len(COMPONENTS)} components this ledger "
             f"binds {COMPONENTS}", EXIT_POINTER)
    tc = token.get("commitments", {})
    if isinstance(tc, dict) and any(isinstance(v, str) and len(v) in (64, 66) and all(c in "0123456789abcdefx" for c in v)
                                    for v in tc.values()):
        fail("token.commitments appears to carry a digest value; it must hold the contract only", EXIT_CARD)

    # Digests of the nine components (raw bytes).
    digests = {name: {"path": rel, **digest_file(repo / rel)} for name, rel in COMPONENTS}

    # Doctrine root — after preflight, all fifteen pointers required.
    root = doctrine_root(persona)

    # Optional image candidate — sha256 only, explicitly unconfirmed, never an ipfs:// URI.
    image_candidate: Optional[Dict[str, Any]] = None
    if image is not None:
        if not image.is_file():
            fail(f"--image {image} is not a file")
        idata = image.read_bytes()
        icid, ireason = cid_or_none(idata)
        try:
            image_path: Optional[str] = image.resolve().relative_to(repo).as_posix()
        except ValueError:
            image_path = None  # outside the repo: the name only, never a host path
        image_candidate = {
            "file": image.name,
            "path": image_path,
            "bytes": len(idata),
            "sha256": sha256_hex(idata),
            "cid": icid,
            "status": "unconfirmed by the operator — a candidate, not the artwork; no ipfs:// URI is synthesised",
        }
        if icid:
            image_candidate["cid_note"] = ("predicted locally (CIDv1 raw, single block); iNFT.md condition 4 takes "
                                           "only the CID an IPFS node returns once pinned, so the card's image "
                                           "stays null until then")
        if ireason:
            image_candidate["cid_reason"] = ireason
        if image_named:
            image_candidate["status"] = ("named by the operator as the artwork — not pinned, so the card's image "
                                         "stays null; no ipfs:// URI is synthesised")
            image_candidate["named_by_operator"] = image_named
            findings.append(f"--image supplied: {image.name} recorded as the operator-NAMED artwork (sha256; not pinned)")
        else:
            findings.append(f"--image supplied: {image.name} recorded as an UNCONFIRMED candidate (sha256 only)")

    chartered, generated_from = git_provenance(repo)

    # §7 inputs, from LOCAL git only: the manifest committed at HEAD, and P when --parent-commit names it.
    def manifest_at(rev: str) -> Optional[Dict[str, Any]]:
        raw = git_bytes(repo, rev, MANIFEST_NAME)
        if raw is None:
            return None
        try:
            m = loads_strict(raw.decode("utf-8"))
        except ValueError as e:
            fail(f"{rev}:{MANIFEST_NAME} is not UTF-8 JSON with unique keys: {e}")
        if not isinstance(m, dict):
            fail(f"{rev}:{MANIFEST_NAME} is not a JSON object")
        return m

    head_prev = manifest_at("HEAD") if generated_from.get("repo_head_commit") else None
    parent_p = None
    if parent_commit is not None:
        parent_p = manifest_at(parent_commit)
        if parent_p is None:
            fail(f"--parent-commit {parent_commit}: no {MANIFEST_NAME} at that revision in this clone "
                 "(the binder never fetches; P must be on disk)")

    # The THOT manifest — N facets, one content-addressed identity (sagi/engine/THOT_MANIFEST.md).
    manifest, manifest_bytes = build_manifest(repo, digests, root, generated_from, persona, derivations,
                                              head_prev, parent_p, parent_reason)

    # Card FIRST — its CID goes into the ledger.
    card = build_card(persona, chartered, generated_from, digests, root, image_candidate, findings)
    card_pre = require_preflight(card, CARD_NAME)
    card_bytes = dump_bytes(card)
    card_cid, card_cid_reason = cid_or_none(card_bytes)
    card_digest = "0x" + keccak256(canonical_bytes(card)).hex()

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / CARD_NAME).write_bytes(card_bytes)

    ledger: Dict[str, Any] = {
        "$comment": ("DERIVED OUTPUT — generated by bind/savante_bind.py; regenerable; never hand-edited. "
                     "This file contains NO digest of itself. It is the ONLY place binding values ever live; "
                     "they are never written back into savante.persona."),
        "schema": "savante.commitments v1",
        "generated_from": generated_from,
        "findings": findings,
        "canonicalization": {
            "declaration": ("files are committed by RAW BYTES (no canonicalization); the doctrine root and the card "
                            "digest are over canonical_bytes, which equals RFC 8785 (JCS) output ONLY under the "
                            "preflight conditions P1 (all property names ASCII) and P2 (all numbers integers within "
                            "+/-2^53). No JCS library is used; the guard is the conformance mechanism."),
            "canonical_bytes": "json.dumps(v, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')",
            "preflight": {
                "P1": "every property name is ASCII",
                "P2": "every JSON number is an integer within +/-2^53",
                "persona": {
                    "property_name_count": pre["property_name_count"],
                    "all_property_names_ascii": pre["all_property_names_ascii"],
                    "numbers": pre["numbers"],
                    "result": "pass",
                },
                "card": {
                    "property_name_count": card_pre["property_name_count"],
                    "all_property_names_ascii": card_pre["all_property_names_ascii"],
                    "numbers": card_pre["numbers"],
                    "result": "pass",
                },
            },
        },
        "file_commitment": {
            "method": "sha256 over raw file bytes; CIDv1 (codec raw 0x55, multihash sha2-256 0x12/0x20, multibase base32 'b') over the same bytes",
            "implementation": ("cid_v1_raw reproduced verbatim from /home/hacker/mindX/mindx/godel/mindxtrain/"
                               "inft_publish.py:39-47 (helper _b32_lower :34-36)"),
            "cid_bound_bytes": CID_MAX_BYTES,
            "cid_bound_source": "inft_publish.py:40-43 — above the bound the IPFS CID depends on chunking; sha256 only",
            "sha256_recovery": "base32-decode the CID after the leading 'b' and strip the 4-byte prefix 01 55 12 20",
        },
        "artifacts": digests,
        "bundle": {
            "path": MANIFEST_NAME,
            "bytes": len(manifest_bytes),
            "file": {
                "sha256": sha256_hex(manifest_bytes),
                "cid": cid_or_none(manifest_bytes)[0],
                "thot": "thot:" + sha256_hex(manifest_bytes),
                "note": ("the identity of the manifest FILE AS WRITTEN — pretty-printed, identity block included. "
                         "This is what `permanence/dapp.mjs identify savante.thot.json` reports and what an Arweave "
                         "upload would store. It NECESSARILY differs from manifest.identity, which is over the "
                         "canonical form WITHOUT the identity block, because a document cannot contain a digest of "
                         "itself. Two hashes, two questions: this one names the stored object, that one names the "
                         "bundle. It lives here because it cannot live in the file it measures."),
            },
            "schema": manifest["schema"],
            "generation": manifest["bundle"]["generation"],
            "parent": manifest["bundle"]["parent"],
            "facets": [f["facet"] for f in manifest["facets"]],
            "absent": [a["facet"] for a in manifest["absent"]],
            "identity": manifest["identity"],
            "bundle_root": manifest["bundle_root"]["value"],
            "merkle_root": manifest["merkle"]["root"],
            "rung": manifest["rung"]["value"],
            "derivations": derivations,
            "note": ("the bundle answers `is this the same bundle?`; the doctrine root below answers `is the office "
                     "still the office?`. Two roots, deliberately separate."),
        },
        "doctrine_root": {
            "value": root["root_hex"],
            "hash": "keccak256",
            "keccak_backend": KECCAK_BACKEND,
            "path_syntax": "RFC 6901 JSON Pointer",
            "pointers": DOCTRINE_POINTERS,
            "construction": CONSTRUCTION_TEXT,
            "separators": {"unit": "0x1f (US) between pointer and value", "record": "0x1e (RS) after each value"},
            "preimage_bytes": root["preimage_bytes"],
            "clauses": root["clauses"],
            "on_edit": ("a changed root is not an error this program can prevent; it is a difference a third "
                        "party can see — compare `clauses[].canonical_sha256` to locate the edited clause"),
        },
        "card": {
            "path": CARD_NAME,
            "bytes": len(card_bytes),
            "versions": {
                "v0": {"cid": card_cid, "sha256": sha256_hex(card_bytes), "registrations": "empty"},
                "v1": None,
            },
            "v1_reason": "v1 (registrations populated) exists only after a mint; nothing is minted",
            "current": "v0",
            "digest": {
                "keccak256_canonical": card_digest,
                "publish_when": ("only if the card is ever served over https:// instead of ipfs://. ERC-8004 defines no "
                                 "hash field for agentURI; keccak256_canonical is recorded for an https:// deployment by "
                                 "analogy with the feedbackHash/responseHash rule (OPTIONAL for content-addressed URIs), "
                                 "not because the EIP asks for it"),
            },
        },
        "onchain_slots": {
            "savantePersonaDigest": {
                "value": "0x" + digests["identity"]["sha256"],
                "bytes": 32,
                "derived_from": "artifacts.identity.sha256",
                "call": "setMetadata(agentId, 'savantePersonaDigest', bytes32)",
                "written": False,
                "written_reason": "nothing is minted; this program has no network",
            },
            "savanteDoctrineRoot": {
                "value": root["root_hex"],
                "bytes": 32,
                "derived_from": "doctrine_root.value",
                "call": "setMetadata(agentId, 'savanteDoctrineRoot', bytes32)",
                "written": False,
                "written_reason": "nothing is minted; this program has no network",
            },
        },
        "bindings": bindings,
        "bindings_rule": ("token.bindings in savante.persona is a schema declaration whose values are permanently null. "
                          "Once a mint happens, agentId / agentURI / chain / contract are recorded in THIS file under "
                          "`mint` and never written back into the persona — that is what keeps savantePersonaDigest "
                          "valid across the whole registration sequence."),
        "mint": None,
        "mint_reason": "not minted, not even dry-run; this binder performs no on-chain action and records none",
        "image_candidate": image_candidate,
        "mirror_check": mirror_report,
    }
    if card_cid_reason:
        ledger["card"]["versions"]["v0"]["cid_reason"] = card_cid_reason

    ledger_bytes = dump_bytes(ledger)
    (out_dir / LEDGER_NAME).write_bytes(ledger_bytes)
    (out_dir / MANIFEST_NAME).write_bytes(manifest_bytes)

    # Summary.
    print(f"wrote {out_dir / CARD_NAME} ({len(card_bytes)} bytes)")
    print(f"wrote {out_dir / LEDGER_NAME} ({len(ledger_bytes)} bytes)")
    print(f"wrote {out_dir / MANIFEST_NAME} ({len(manifest_bytes)} bytes)")
    for name, d in digests.items():
        print(f"{name:9s} {d['path']}  {d['bytes']} B  sha256 {d['sha256']}  cid {d['cid']}")
    print(f"doctrine_root {root['root_hex']}  (preimage {root['preimage_bytes']} B, {len(DOCTRINE_POINTERS)} pointers)")
    print(f"card_cid      {card_cid}")
    print(f"card_digest   {card_digest}")
    print(f"chartered     {chartered['date']}  head {generated_from['repo_head_commit']}")
    print(f"generation    {manifest['bundle']['generation']}  parent {manifest['bundle']['parent']}  "
          f"identity {manifest['identity']['cid']}")
    if generated_from["components_differing_from_head"]:
        print(f"note: working tree differs from HEAD for {generated_from['components_differing_from_head']}")
    for f in findings:
        print(f"FINDING: {f}")
    return EXIT_OK


# ── self-test ─────────────────────────────────────────────────────────────────

def self_test() -> int:
    ok = True

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal ok
        ok = ok and cond
        print(f"[{'PASS' if cond else 'FAIL'}] {name}{(' — ' + detail) if detail else ''}")

    # 1. keccak
    if KECCAK is None:
        check("keccak backend available", False, "neither pycryptodome nor eth_utils importable")
    else:
        got = keccak256(b"").hex()
        check("keccak256(b'') self-test", got == KECCAK_EMPTY_HEX, f"{KECCAK_BACKEND}: {got}")
        try:
            import hashlib as _h
            check("hashlib.sha3_256 differs from keccak (would be the wrong hash)",
                  _h.sha3_256(b"").hexdigest() != got)
        except Exception:
            pass

    # 2. CID against the reference implementation
    hello = b"hello"
    ours = cid_v1_raw(hello)
    ref_dir = Path("/home/hacker/mindX/mindx/godel/mindxtrain")
    ref_cid = None
    if (ref_dir / "inft_publish.py").is_file():
        sys.path.insert(0, str(ref_dir))
        try:
            import inft_publish  # type: ignore
            ref_cid = inft_publish.cid_v1_raw(hello)
        except Exception as e:  # pragma: no cover
            print(f"[SKIP] inft_publish import failed: {e}")
        finally:
            sys.path.pop(0)
    if ref_cid is not None:
        check("cid_v1_raw(b'hello') == inft_publish.cid_v1_raw(b'hello')", ours == ref_cid, ours)
    else:
        print(f"[SKIP] reference inft_publish not importable; cid_v1_raw(b'hello') = {ours}")
    # structural: decode and recover sha256
    raw = base64.b32decode(ours[1:].upper() + "=" * (-len(ours[1:]) % 8))
    check("CID prefix 01 55 12 20 and sha256 recoverable", raw[:4] == bytes([1, 0x55, 0x12, 0x20])
          and raw[4:] == hashlib.sha256(hello).digest())
    cid, reason = cid_or_none(b"x" * (CID_MAX_BYTES + 1))
    check("CID refused above 256 KiB", cid is None and reason is not None)
    cid, reason = cid_or_none(b"x" * CID_MAX_BYTES)
    check("CID emitted at exactly 256 KiB", cid is not None and reason is None)

    # 3. preflight
    check("preflight fails on a float", not preflight({"a": {"b": [1, 2.5]}})["ok"],
          str(preflight({"a": {"b": [1, 2.5]}})["errors"]))
    check("preflight fails on a non-ASCII property name", not preflight({"café": 1})["ok"],
          str(preflight({"café": 1})["errors"]))
    check("preflight fails on an integer beyond 2^53", not preflight({"n": 2 ** 53 + 1})["ok"])
    good = preflight({"a": 4, "b": [True, None, "é in a value is fine"]})
    check("preflight passes on integers, bools, nulls, non-ASCII values", good["ok"] and good["numbers"] == [{"pointer": "/a", "value": 4}])
    check("pointer escaping", preflight({"a/b": {"c~d": 1.5}})["errors"][0]["pointer"] == "/a~1b/c~0d")

    # 4. RFC 6901
    doc = {"a": {"b": [10, {"c~d": "x"}]}, "m/n": 1}
    check("resolve nested + escaped", resolve(doc, "/a/b/1/c~0d") == "x" and resolve(doc, "/m~1n") == 1)
    try:
        resolve(doc, "/a/zzz")
        check("missing pointer raises", False)
    except PointerMissing:
        check("missing pointer raises", True)

    # 5. doctrine root determinism and order sensitivity
    fixture = {p.split("/")[1]: None for p in DOCTRINE_POINTERS}
    fixture.update({
        "persona": "t", "name": "T", "source": "s", "format": "f", "system_prompt": "p", "mantra": "m", "oath": "o",
        "bdi": {"beliefs": [{"id": "x", "belief": "y"}]},
        "skills": {"primary": "p", "taxonomy": {"verdicts": ["A", "D"]}, "defer_triggers": ["t"], "validation": {"invariants": 4}},
        "safety": {"scope": "s"}, "embodiment": {"x": None},
        "token": {"intelligence": {"tool_allowlist": ["Read", "Grep", "Glob", "Bash"]}},
    })
    r1 = doctrine_root(fixture)["root_hex"]
    r2 = doctrine_root(fixture)["root_hex"]
    check("doctrine root deterministic", r1 == r2, r1)
    swapped = dict(fixture)
    swapped["token"] = {"intelligence": {"tool_allowlist": ["Read", "Grep", "Glob", "Bash", "Edit"]}}
    check("doctrine root changes when the allowlist gains Edit", doctrine_root(swapped)["root_hex"] != r1)
    pre_i = b"".join(p.encode() + b"\x1f" + canonical_bytes(resolve(fixture, p)) + b"\x1e" for p in DOCTRINE_POINTERS)
    check("preimage construction matches spec §3.2 literally", "0x" + keccak256(pre_i).hex() == r1)
    check("canonical_bytes sorts keys and strips whitespace", canonical_bytes({"b": 1, "a": [1, "é"]}) == b'{"a":[1,"\xc3\xa9"],"b":1}')

    # 6. §5 Merkle and bundle_root: the spec's test vector (savante.thot.json @ 1fcca89), and fail > 64
    if KECCAK is not None:
        v1 = [("persona", "5c2402cc01b4fc4137f3f3ad34710fc0ffc6361faaa32c0251d4849327006009"),
              ("agent", "3cdd31d9734d5815da53411fa31650665b7dde0c348da4ac50ad7bf686fc75f0"),
              ("model", "03dbbf5069cfdbcd67747eff1a513217b8139e16e0b4cc74aa71015adb9d3581"),
              ("prompt", "baf5a302bf591b977d45ff21c484cc1279c9693e0f65ae9541db42c042bdcffe"),
              ("tool", "ebd3ec9342801ae3dc72840db55e7052b33ff487b6b1fa2e3145e69d9da9ece4"),
              ("skill", "350da6fcf3cc09eb60516317438f7d3f954a83a8d1f526d9f2e9268a0cf4d6fe"),
              ("voaice", "d4619d4c6fcf0913ed0e2a1616eb219d2bff9a22efbb323a7e579cf44e25862e"),
              ("faice", "6e2d33f8e6ad06e56c254549020643ab70b55cb61a6cb0328751ba33b7e3991f")]
        recs = [f.encode("utf-8") + b"\x1f" + h.encode("ascii") for f, h in v1]
        check("§5 test vector bundle_root (savante @ 1fcca89)",
              "0x" + keccak256(b"".join(r + b"\x1e" for r in recs)).hex()
              == "0x235da8e993dc8af2c077f50d698962446b872b17b1e5b033d5c5d976532b8880")
        check("§5 test vector merkle root (savante @ 1fcca89)",
              merkle_root([keccak256(r) for r in recs])
              == "0xdc1d80957cf831aee6638fd569e22cf0f6e5a1ec99ddde91cfecb5a15408fbe1")
        try:
            merkle_root([keccak256(b"x")] * (MERKLE_LEAVES + 1))
            check("merkle_root fails on 65 leaves rather than truncating", False)
        except ValueError:
            check("merkle_root fails on 65 leaves rather than truncating", True)

    # 7. §3a closed vocabulary: the emitted block passes; every refusal case refuses
    base = {"schema": SCHEMA, "algorithms": manifest_algorithms(), "doctrine_root": "0x" + "00" * 32,
            "facets": [], "custom": []}
    check("emitted algorithms block is accepted", algorithms_refusals(base) == [], str(algorithms_refusals(base)))

    def mutated(fn: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
        m = json.loads(json.dumps(base))
        fn(m)
        return m

    cases: List[Tuple[str, Callable[[Dict[str, Any]], None]]] = [
        ("missing block", lambda m: m.pop("algorithms")),
        ("block not an object", lambda m: m.__setitem__("algorithms", ["sha256"])),
        ("unknown key", lambda m: m["algorithms"].__setitem__("facet_digest_v2", "blake3")),
        ("canonicalisation without .encode('utf-8')", lambda m: m["algorithms"].__setitem__(
            "canonicalisation", "json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=False)")),
        ("doctrine_root missing while the manifest carries one", lambda m: m["algorithms"].pop("doctrine_root")),
        ("git_blob missing while a facet is named by a git blob",
         lambda m: m["facets"].append({"facet": "voaice", "git_blob": "0" * 40})),
        ("git_blob with a different value", lambda m: m["algorithms"].__setitem__("git_blob", "sha1")),
        ("schema missing", lambda m: m.pop("schema")),
        ("schema sagi.thot_manifest/2", lambda m: m.__setitem__("schema", "sagi.thot_manifest/2")),
        ("note is not a string", lambda m: m["algorithms"].__setitem__("note", {"x": 1})),
        ("note is null", lambda m: m["algorithms"].__setitem__("note", None)),
        ("G +1 facets[5].reference.git_blob_sha1 without the declaration",
         lambda m: m["facets"].extend([{"facet": f"f{i}"} for i in range(5)] + [{"facet": "voaice", "reference": {"git_blob_sha1": "bf" * 20}}])),
        ("G +2 facets[0].git_blob (value null still counts)",
         lambda m: m["facets"].append({"facet": "persona", "git_blob": None})),
        ("G +3 custom[0].source.git_blob_id", lambda m: m["custom"].append({"facet": "x-a.b", "source": {"git_blob_id": "x"}})),
        ("G +4 facets[2].renderings[1].git_blob_sha1",
         lambda m: m["facets"].extend([{}, {}, {"renderings": [{}, {"git_blob_sha1": "ab" * 20}]}])),
    ]
    for k in ALGORITHMS_ALWAYS:
        cases.append((f"{k} missing", lambda m, k=k: m["algorithms"].pop(k)))
        cases.append((f"{k} = sha3-256", lambda m, k=k: m["algorithms"].__setitem__(k, "sha3-256")))
    cases.append(("doctrine_root = sha3-256", lambda m: m["algorithms"].__setitem__("doctrine_root", "sha3-256")))
    for label, fn in cases:
        r = algorithms_refusals(mutated(fn))
        check(f"algorithms refused: {label}", bool(r), r[0] if r else "NOT refused")
    no_root = mutated(lambda m: (m.pop("doctrine_root"), m["algorithms"].pop("doctrine_root")))
    check("doctrine_root key not required when the manifest carries no doctrine_root", algorithms_refusals(no_root) == [])
    check("a changed note is not an algorithm", algorithms_refusals(mutated(
        lambda m: m["algorithms"].__setitem__("note", "anything"))) == [])
    check("git_blob declared with the exact §3a value is accepted", algorithms_refusals(mutated(
        lambda m: m["algorithms"].__setitem__("git_blob", ALGORITHMS_CONDITIONAL["git_blob"]))) == [])
    check("a facet named by sha256 under `sha256` does not require git_blob", algorithms_refusals(mutated(
        lambda m: m["facets"].append({"facet": "persona", "sha256": "ab" * 32}))) == [])
    # §3a condition G negatives: none may require git_blob (a verifier MUST NOT widen G).
    for label, fn in [
        ("G -1 facets[5].reference.commit = 40-hex", lambda m: m["facets"].extend(
            [{} for _ in range(5)] + [{"reference": {"commit": "3f7412" + "0" * 30 + "6c76"}}])),
        ("G -2 rung.evidence.locator names a commit", lambda m: m.__setitem__(
            "rung", {"evidence": {"locator": "github.com/cryptoAGI/savante@368c7322f2c66e470b28e1673bf5a0e5ced124d4"}})),
        ("G -3 relations[0].manifest_commit", lambda m: m.__setitem__("relations", [{"manifest_commit": "8b57ccf"}])),
        ("G -4 facets[1].reference.git_object and facets[1].oid = 40 hex", lambda m: m["facets"].extend(
            [{}, {"reference": {"git_object": "ab" * 20}, "oid": "cd" * 20}])),
        ("G -5 absent[0].git_blob_sha1 and references[0].git_blob_sha1", lambda m: (
            m.__setitem__("absent", [{"git_blob_sha1": "ab" * 20}]), m.__setitem__("references", [{"git_blob_sha1": "ab" * 20}]))),
        ("G -6 algorithms.git_blob does not trigger itself", lambda m: m["algorithms"].__setitem__(
            "git_blob", ALGORITHMS_CONDITIONAL["git_blob"])),
        ("G -7 facets[0].note = 'git_blob_sha1 bfcc5e…' (a value, not a key)",
         lambda m: m["facets"].append({"note": "git_blob_sha1 bfcc5e"})),
        ("G substring only: facets[0].x_git_blob", lambda m: m["facets"].append({"x_git_blob": "ab" * 20})),
        ("G case-sensitive: facets[0].GIT_BLOB", lambda m: m["facets"].append({"GIT_BLOB": "ab" * 20})),
    ]:
        mm = mutated(fn)
        check(f"not required: {label}", not git_blob_condition(mm) and algorithms_refusals(mm) == [],
              str(algorithms_refusals(mm)))

    # 8. §7 generations: decide_bundle (G1-G5), pure, against synthetic manifests.
    def mf(facets: Dict[str, str], gen: int = 1, parent: Optional[str] = None, rung: str = "referenced",
           reason: str = GENESIS_REASON, bid: str = BUNDLE_ID) -> Dict[str, Any]:
        m = {"schema": SCHEMA, "algorithms": manifest_algorithms(),
             "bundle": {"id": bid, "officer": "Savante", "generation": gen, "parent": parent, "parent_reason": reason},
             "facets": [{"facet": k, "sha256": v, "state": "present"} for k, v in facets.items()], "custom": [],
             "rung": {"value": rung}}
        m["identity"] = {"cid": manifest_identity_cid(m)}
        return m
    g1 = mf({"persona": "aa", "agent": "bb"})
    edited = mf({"persona": "cc", "agent": "bb"})
    blk, why = decide_bundle(edited, None, None, None)
    check("G1 no manifest at HEAD, no parent: genesis", why is None and blk == {"generation": 1, "parent": None,
                                                                              "parent_reason": GENESIS_REASON}, str(why))
    blk, why = decide_bundle(mf({"persona": "aa", "agent": "bb"}), g1, None, None)
    check("G4 no facet change since HEAD: generation and parent carried", why is None and blk["generation"] == 1, str(why))
    blk, why = decide_bundle(edited, g1, None, None)
    check("G5 facet change without --parent-commit is refused", blk is None and why.startswith("G5"), str(why))
    blk, why = decide_bundle(edited, g1, g1, "persona edited")
    check("G2 facet change with P: generation 2, parent = P.identity.cid",
          why is None and blk == {"generation": 2, "parent": g1["identity"]["cid"], "parent_reason": "persona edited"}, str(why))
    check("G2 parent_reason required", decide_bundle(edited, g1, g1, " ")[0] is None)
    check("G2 --parent-reason without --parent-commit refused", decide_bundle(edited, g1, None, "x")[0] is None)
    check("G4 --parent-commit with no facet change refused", decide_bundle(mf({"persona": "aa", "agent": "bb"}), g1, g1, "x")[0] is None)
    check("G2 P of another bundle refused", decide_bundle(edited, g1, mf({"persona": "aa"}, bid="jaimla"), "x")[0] is None)
    tampered = json.loads(json.dumps(g1))
    tampered["identity"]["cid"] = "bafkrei" + "a" * 52
    check("G2 P whose file does not reproduce its identity.cid refused", decide_bundle(edited, g1, tampered, "x")[0] is None)
    g2 = mf({"persona": "cc", "agent": "bb"}, gen=2, parent=g1["identity"]["cid"], reason="persona edited")
    blk, why = decide_bundle(mf({"persona": "cc", "agent": "bb"}), g2, g1, "persona edited")
    check("re-bind of generation 2 at a later HEAD with the same P keeps generation 2",
          why is None and blk["generation"] == 2 and blk["parent"] == g1["identity"]["cid"], str(why))
    blk, why = decide_bundle(mf({"persona": "cc", "agent": "bb"}), g2, None, None)
    check("G4 plain re-bind over a committed generation 2 carries it forward",
          why is None and blk == {"generation": 2, "parent": g1["identity"]["cid"], "parent_reason": "persona edited"}, str(why))
    check("G5 a further facet change over a committed generation 2 with P = genesis refused",
          decide_bundle(mf({"persona": "dd", "agent": "bb"}), g2, g1, "x")[0] is None)
    check("P that is not the most recent manifest refused",
          decide_bundle(edited, mf({"persona": "zz"}, gen=3, parent="bafkrei" + "b" * 52, reason="r"), g1, "x")[0] is None)
    check("G4 anchored manifest at HEAD is never re-bound",
          decide_bundle(mf({"persona": "aa", "agent": "bb"}), mf({"persona": "aa", "agent": "bb"}, rung="committed"), None, None)[0] is None)
    succ = json.loads(json.dumps(g1))
    succ["algorithms"]["facet_digest"] = "blake3"
    check("G3 a changed algorithm value is a successor", successor_change(g1, succ) and not successor_change(g1, g1))
    no_dr = json.loads(json.dumps(g1))
    no_dr["algorithms"].pop("doctrine_root")
    check("G4 adding algorithms.doctrine_root with its v1 value is not a successor", not successor_change(no_dr, g1))
    check("locator form S10", bool(LOCATOR_RE.match("github.com/cryptoAGI/savante@" + "1f" * 20))
          and not LOCATOR_RE.match("github.com/cryptoAGI/savante@1fcca89") and not LOCATOR_RE.match("github.com/x/y@None"))
    try:
        loads_strict('{"algorithms": {"merkle_pad": "sha3-256", "merkle_pad": "keccak256"}}')
        check("loads_strict refuses a duplicate key", False)
    except DuplicateKey:
        check("loads_strict refuses a duplicate key", True)
    check("loads_strict accepts the same key in two different objects",
          loads_strict('{"a": {"k": 1}, "b": {"k": 2}}') == {"a": {"k": 1}, "b": {"k": 2}})

    print("self-test:", "OK" if ok else "FAILED")
    return EXIT_OK if ok else EXIT_GENERIC


def main(argv: Optional[List[str]] = None) -> int:
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Derive savante.agentcard.json, savante.commitments.json and savante.thot.json. Operator tool; no network.")
    ap.add_argument("--repo", type=Path, default=here, help=f"repo root (default: {here})")
    ap.add_argument("--out-dir", type=Path, default=None, help="where to write the three derived files (default: repo root)")
    ap.add_argument("--mirror", type=Path, default=DEFAULT_MIRROR, help=f"mindX mirror of savante.persona (default: {DEFAULT_MIRROR})")
    ap.add_argument("--no-mirror-check", action="store_true", help="skip the mirror md5 check; recorded in the output as a finding")
    ap.add_argument("--image", type=Path, default=None, help="candidate artwork: sha256 recorded as UNCONFIRMED; never an ipfs:// URI")
    ap.add_argument("--parent-commit", default=None, metavar="REV",
                    help="bind the next generation (THOT_MANIFEST.md §7): P = savante.thot.json at REV in this LOCAL "
                         "clone (never fetched); bundle.parent = P's identity.cid, generation = P's + 1. Without it, "
                         "HEAD's manifest is carried forward (G4) and a facet change is refused (G5)")
    ap.add_argument("--parent-reason", default=None, metavar="TEXT",
                    help="with --parent-commit: bundle.parent_reason, what changed since P (required, never compared)")
    ap.add_argument("--image-named", default=None, metavar="EVIDENCE",
                    help="with --image: the operator named this file as the artwork (iNFT.md condition 4); EVIDENCE says "
                         "where that naming is recorded. Without it the image stays an UNCONFIRMED candidate")
    ap.add_argument("--self-test", action="store_true", help="run the keccak / CID / preflight / pointer / §3a / §7 self-tests and exit")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if a.parent_reason is not None and a.parent_commit is None:
        ap.error("--parent-reason requires --parent-commit")
    if a.image_named is not None and a.image is None:
        ap.error("--image-named requires --image")
    repo = a.repo.resolve()
    out_dir = (a.out_dir or repo).resolve()
    if out_dir == repo and (repo / "savante.persona").resolve() in ((out_dir / CARD_NAME).resolve(), (out_dir / LEDGER_NAME).resolve()):
        fail("refusing to write over savante.persona")  # structurally impossible, kept as a stated invariant
    return run_bind(repo, out_dir, a.mirror.resolve() if a.mirror else DEFAULT_MIRROR, a.no_mirror_check, a.image,
                    a.parent_commit, a.parent_reason, a.image_named)


if __name__ == "__main__":
    sys.exit(main())
