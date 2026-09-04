#!/usr/bin/env python3
"""bind/savante_bind.py — the OPERATOR's binder. Savante audits this file and never runs it.

Derives, from savante.persona, the two .claude/ files and the two sAGI class facets
(sAGI.agent, sAGI.model — five components), the two DERIVED artifacts:

    savante.agentcard.json    — the public face (EIP-721 metadata + ERC-8004 registration-v1)
    savante.commitments.json  — the integrity ledger (raw-byte digests + the doctrine root)

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
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
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
]

CARD_NAME = "savante.agentcard.json"
LEDGER_NAME = "savante.commitments.json"

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
        "generated_from": generated_from,
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


# ── main ──────────────────────────────────────────────────────────────────────

def run_bind(repo: Path, out_dir: Path, mirror: Path, no_mirror_check: bool, image: Optional[Path]) -> int:
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
    tc = token.get("commitments", {})
    if isinstance(tc, dict) and any(isinstance(v, str) and len(v) in (64, 66) and all(c in "0123456789abcdefx" for c in v)
                                    for v in tc.values()):
        fail("token.commitments appears to carry a digest value; it must hold the contract only", EXIT_CARD)

    # Digests of the five components (raw bytes).
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
        image_candidate = {
            "file": image.name,
            "bytes": len(idata),
            "sha256": sha256_hex(idata),
            "cid": icid,
            "status": "unconfirmed by the operator — a candidate, not the artwork; no ipfs:// URI is synthesised",
        }
        if ireason:
            image_candidate["cid_reason"] = ireason
        findings.append(f"--image supplied: {image.name} recorded as an UNCONFIRMED candidate (sha256 only)")

    chartered, generated_from = git_provenance(repo)

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

    # Summary.
    print(f"wrote {out_dir / CARD_NAME} ({len(card_bytes)} bytes)")
    print(f"wrote {out_dir / LEDGER_NAME} ({len(ledger_bytes)} bytes)")
    for name, d in digests.items():
        print(f"{name:9s} {d['path']}  {d['bytes']} B  sha256 {d['sha256']}  cid {d['cid']}")
    print(f"doctrine_root {root['root_hex']}  (preimage {root['preimage_bytes']} B, {len(DOCTRINE_POINTERS)} pointers)")
    print(f"card_cid      {card_cid}")
    print(f"card_digest   {card_digest}")
    print(f"chartered     {chartered['date']}  head {generated_from['repo_head_commit']}")
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

    print("self-test:", "OK" if ok else "FAILED")
    return EXIT_OK if ok else EXIT_GENERIC


def main(argv: Optional[List[str]] = None) -> int:
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description="Derive savante.agentcard.json and savante.commitments.json. Operator tool; no network.")
    ap.add_argument("--repo", type=Path, default=here, help=f"repo root (default: {here})")
    ap.add_argument("--out-dir", type=Path, default=None, help="where to write the two derived files (default: repo root)")
    ap.add_argument("--mirror", type=Path, default=DEFAULT_MIRROR, help=f"mindX mirror of savante.persona (default: {DEFAULT_MIRROR})")
    ap.add_argument("--no-mirror-check", action="store_true", help="skip the mirror md5 check; recorded in the output as a finding")
    ap.add_argument("--image", type=Path, default=None, help="candidate artwork: sha256 recorded as UNCONFIRMED; never an ipfs:// URI")
    ap.add_argument("--self-test", action="store_true", help="run the keccak / CID / preflight / pointer self-tests and exit")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    repo = a.repo.resolve()
    out_dir = (a.out_dir or repo).resolve()
    if out_dir == repo and (repo / "savante.persona").resolve() in ((out_dir / CARD_NAME).resolve(), (out_dir / LEDGER_NAME).resolve()):
        fail("refusing to write over savante.persona")  # structurally impossible, kept as a stated invariant
    return run_bind(repo, out_dir, a.mirror.resolve() if a.mirror else DEFAULT_MIRROR, a.no_mirror_check, a.image)


if __name__ == "__main__":
    sys.exit(main())
