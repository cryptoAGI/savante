"""Savante — the oversight office as a Gradio surface. Read-only by charter, and the UI proves it.

`savante === sAGI.agent`. Savante is not a model: it is a **charter run on a frontier model** under a
harness whose tool allowlist is Read, Grep, Glob and Bash — no Edit, no Write, no Agent, because
"granting any of them voids the office" (`sAGI.agent:45`). Its doctrine is seven words long: *the
structural substrate — rarely intervenes, always watching.* Its epistemology has two states and no
third: a claim is **known** when it survives verification against evidence, and **unknown** otherwise.
It holds no opinions; it holds findings.

So this surface is not an agent console. Six rooms, each something the office may actually do:

- **The Office** — the charter itself, read from `savante.persona`: mantra, oath, the four verdicts,
  the tool allowlist, and the mint status, which is `not_yet_minted` and stays that way here.
- **Evidence** — verification *executed*: run the tests, read the git state, grep for the capability a
  document asserts. Read-only verbs only, actual results only, refusals that state their reason. This
  is what makes Savante not a linter: a linter checks rules, Savante checks claims.
- **Verdict** — the fixed five-field contract (FINDINGS · VERDICT · RATIONALE · CONDITIONS · RISKS
  WATCHED). The composer **refuses to render APPROVE with no evidence rows**, because "I never approve
  what I have not read" is the oath.
- **Integrity** — recompute the bundle's sha256 and CIDv1 from the bytes on disk and compare them with
  `savante.commitments.json`. What a holder receives is the ability to prove, without trusting the
  author, that DEFER is still in the vocabulary.
- **Rungs** — the training ladder as *plan only*: Qwen3 8B and the 27B mid-grade, with the hardware each
  needs, what it would cost, and the ceiling and flag that stand between the plan and a charge.
- **Kimi** — a provider configuration tab: base URL, model id, whether a key is present (never the key),
  and a live model list, because model identifiers rot and the provider's own endpoint is the authority.

**There is no mint button, and its absence is the feature.** `iNFT.md` renders `VERDICT: DEFER` on
binding this office to a token, and minting, listing on AgenticPlace, binding a vault and registering on
an ERC-8004 registry are factory steps that wait on the operator's signature (`sAGI.agent:41-44`).

**Lineage of the look.** The palette, the pill strip and the Gradio-compat guards come from the house's
own Space, `mindXhfgradio` (<https://gregory-l-mindxhfgradio.hf.space/>), inlined here rather than
imported so this repository depends on nothing but `gradio`. Three of those guards exist because three
separate versions broke: Gradio 6 moved `theme`/`css` to `launch()`, dropped `type=` from `Chatbot`, and
dropped `show_copy_button` from `Textbox`. The rule learned: **read the installed signature, never pin a
major.**

    SAVANTE_ROOT=~/savante python ui.py          # http://127.0.0.1:7863
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VERSION = "0.2.0"
VERDICTS = ["APPROVE", "APPROVE_WITH_CONDITIONS", "REJECT", "DEFER"]

BUNDLE = ["savante.persona", ".claude/agents/savante.md", ".claude/skills/sagi/SKILL.md",
          "sAGI.agent", "sAGI.model", "savante.agentcard.json", "savante.commitments.json"]

# Read-only verification only. The harness enforces the charter, never trust, and that rule does not
# weaken because the caller is a web page.
SAFE_VERBS = {"pytest", "python", "python3", "git", "grep", "rg", "ls", "cat", "head", "tail", "wc",
              "sha256sum", "find", "node", "forge", "npm", "ruff", "mypy", "gh"}
FORBIDDEN = {"rm", "mv", "cp", "dd", "mkfs", "chmod", "chown", "curl", "wget", "ssh", "scp", "rsync",
             "sudo", "kill", "pkill", "systemctl", "docker", "pip", "uv"}

# ── the ladder, as plan only ───────────────────────────────────────────────────
# Figures read from mindX data/config/hf_capacity.json (2026-09). They are ASSUMPTIONS until a settled
# job replaces them with measured minutes, and the row says so. Nothing here can spend anything: the
# rented lanes need MINDX_HF_ALLOW_PAID on the node AND the per-generation ceiling to hold.
CEILING_USD_PER_GENERATION = 2.00
CEILING_USD_PER_DAY = 5.00
RUNGS: List[Dict[str, Any]] = [
    {"rung": "q3-8b-base", "params": "8B", "lane": "cpu_rented",
     "hardware": "HF Jobs cpu-upgrade / cpu-xl", "vram": "—",
     "cost": "≈$0.03/h — the CPU-imprint continuation past what the VPS holds",
     "state": "PLAN ONLY · needs MINDX_HF_ALLOW_PAID", "why": "same recipe, same imprint gate, priced per minute"},
    {"rung": "q3-8b", "params": "8B", "lane": "cpu_rented / gpu",
     "hardware": "cpu-xl, or t4 / l4x1 if routed to GPU", "vram": "16 GB class",
     "cost": "within the $2.00/generation ceiling on a small GPU",
     "state": "PLAN ONLY · dry_run only", "why": "the next rung up from the 135M actor; CPU-first by doctrine"},
    {"rung": "q3.8-27b", "params": "27B", "lane": "gpu",
     "hardware": "a100-large (80 GB) or rtx-pro-6000 (96 GB)", "vram": "80–96 GB",
     "cost": "≈$1.90 on A100 at 45 min — AT the $2.00/generation ceiling",
     "state": "PLAN ONLY · GPU only, nothing armed", "why": "the mid-grade: what no CPU should attempt"},
    {"rung": "q3.8-27b-fp8", "params": "27B (FP8)", "lane": "gpu",
     "hardware": "l40sx1 (48 GB) at ≈$1.80/h", "vram": "48 GB",
     "cost": "cheaper card, but FP8 base training needs a dequantised path",
     "state": "EXPERIMENTAL · plan only", "why": "30.8 GB checkpoint fits a 48 GB card"},
]


def rung_rows() -> List[List[Any]]:
    return [[r["rung"], r["params"], r["lane"], r["hardware"], r["vram"], r["cost"], r["state"], r["why"]]
            for r in RUNGS]


def rung_note() -> str:
    armed = os.environ.get("MINDX_HF_ALLOW_PAID") == "1"
    return (f"<div class='sv-kv'><span>ceilings</span><span>${CEILING_USD_PER_GENERATION:.2f} per generation · "
            f"${CEILING_USD_PER_DAY:.2f} per day</span>"
            f"<span>paid lane</span><span>{'ARMED on this host' if armed else 'not armed — MINDX_HF_ALLOW_PAID is unset, so no rung below can charge anything'}</span>"
            f"<span>doctrine</span><span>CPU is standing capacity and originates the model; rented GPU is the episodic "
            f"scale-up. A plan that beats a proven baseline gets run — the baseline here is a 135M actor "
            f"trained on 2 vCPU.</span>"
            f"<span>honesty</span><span>every duration is an assumption until a settled job replaces it with "
            f"measured minutes</span></div>")


# ── Kimi (Moonshot) provider configuration ─────────────────────────────────────
# Configuration, not a verdict engine. A model's prose is never a finding: the office renders verdicts
# from evidence it read, and a draft is a draft. Model identifiers rot, so the list endpoint is the
# authority and the field stays editable — the same rule that governs every other provider here.
KIMI = {
    "name": "kimi",
    "vendor": "Moonshot AI",
    "style": "openai-compatible",
    "bases": ["https://api.moonshot.ai/v1", "https://api.moonshot.cn/v1"],
    "env": ["MOONSHOT_API_KEY", "KIMI_API_KEY"],
    "default_model": "kimi-k2-0905-preview",
    "note": "OpenAI-compatible chat completions. Two hosts exist (international and CN); pick the one "
            "your key was issued for. Long-context variants are published under moonshot-v1-* names.",
}


def kimi_key() -> Optional[str]:
    for e in KIMI["env"]:
        v = os.environ.get(e)
        if v and v.strip():
            return v.strip()
    return None


def kimi_status() -> str:
    k = kimi_key()
    which = next((e for e in KIMI["env"] if os.environ.get(e)), None)
    return (f"<div class='sv-kv'><span>vendor</span><span>{KIMI['vendor']} · {KIMI['style']}</span>"
            f"<span>key</span><span>{'present via <code>' + which + '</code>' if k else 'absent — set ' + ' or '.join(KIMI['env'])}</span>"
            f"<span>hosts</span><span>{' · '.join(KIMI['bases'])}</span>"
            f"<span>rule</span><span>the key is never printed, returned or logged; only whether one exists</span>"
            f"<span>standing</span><span>a model's prose is a draft, never a finding — the office renders "
            f"verdicts from evidence it read</span></div>")


def kimi_models(base: str) -> str:
    """Ask the provider what it serves. Model lists rot; this is the authority, not a hardcoded list."""
    k = kimi_key()
    if not k:
        return json.dumps({"ok": False, "reason": f"no key — set {' or '.join(KIMI['env'])}"}, indent=1)
    req = urllib.request.Request(base.rstrip("/") + "/models", headers={"Authorization": f"Bearer {k}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        ids = sorted(str(d.get("id")) for d in (data.get("data") or []) if d.get("id"))
        return json.dumps({"ok": True, "base": base, "count": len(ids), "models": ids}, indent=1)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        hint = ("the key may belong to the other host — .ai and .cn issue separately"
                if e.code in (401, 403) else "")
        return json.dumps({"ok": False, "status": e.code, "body": body, "hint": hint}, indent=1)
    except Exception as e:  # noqa: BLE001
        return json.dumps({"ok": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}, indent=1)


def kimi_ask(base: str, model: str, system: str, prompt: str, temperature: float, max_tokens: int) -> Tuple[str, str]:
    """One prompt, one answer, labelled a DRAFT. Returns (text, meta-as-json)."""
    k = kimi_key()
    if not k:
        return (f"No key. Set {' or '.join(KIMI['env'])} and reload.", "{}")
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    body = json.dumps({"model": model or KIMI["default_model"], "messages": msgs,
                       "temperature": temperature, "max_tokens": int(max_tokens)}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {k}"})
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            obj = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return (f"{KIMI['vendor']} answered {e.code}:\n\n```\n{e.read().decode('utf-8', errors='replace')[:400]}\n```", "{}")
    except Exception as e:  # noqa: BLE001
        return (f"could not reach {base}: {type(e).__name__}: {str(e)[:200]}", "{}")
    text = ((obj.get("choices") or [{}])[0].get("message") or {}).get("content", "")
    u = obj.get("usage") or {}
    meta = {"model": obj.get("model"), "prompt_tokens": u.get("prompt_tokens"),
            "completion_tokens": u.get("completion_tokens"), "total_tokens": u.get("total_tokens"),
            "seconds": round(time.monotonic() - t0, 2),
            "standing": "DRAFT — not a finding and not a verdict"}
    return (text, json.dumps(meta, indent=1))


# ── voaice: the verdict read aloud, adapted from the rage player ───────────────
# Verified from DeltaVerse/ollywoo/voicey.js rather than assumed. Two lanes, and the reason there are
# two is cost: a persona's own lines are PRE-RENDERED, so auditioning the cast is ten file reads and no
# synthesis, while free text is synthesised and therefore bounded — 240 characters, twenty a minute,
# one slot at a time. Bounded, not refused, is the house's rule for an expensive surface.
#
#   voaice      GET  <endpoint>?[text=]&[persona=]&[voice=]&[ref=]   — omit text for the pre-rendered line
#   docsplayer  POST /docsplayer/render {url,title,voice,formats,blocks,job,recipe?}
#               → 202 + {job} → poll /progress?job= → /render/<key> → parts[].url
#
# The id list is copied from `isDocsplayerVoice`, so it is the real roster and not a guess.
VOAICE_VOICES = ["sagi", "neural", "jaimla", "leaderofearth", "overlord", "sam", "ancient",
                 "voicebox", "zen", "classic", "kitt", "t800", "fairydust", "translator", "mony"]
VOAICE_TEXT_CAP = 240


def _first_line(markdown: str) -> str:
    """The first sentence of a rendered verdict — what a voice with a 240-character cap can actually say.

    A verdict is a document; a spoken line is a line. Rather than truncate mid-word and pretend, this
    takes the verdict header or the first real sentence and stops at the cap on a word boundary.
    """
    text = " ".join(str(markdown or "").split())
    if not text:
        return ""
    for marker in ("## VERDICT:", "# Savante —"):
        if marker in text:
            seg = text.split(marker, 1)[1]
            text = (marker.replace("##", "").replace("#", "").strip() + " " + seg).strip()
            break
    text = text.replace("*", "").replace("`", "")
    cut = text[:VOAICE_TEXT_CAP]
    return cut if len(text) <= VOAICE_TEXT_CAP else cut.rsplit(" ", 1)[0] + "…"


def voaice_link(endpoint: str, text: str, persona: str, voice: str) -> str:
    """Build the audition request and say exactly what it will cost.

    Deliberately a link rather than a fetch: the endpoint is another origin, and a verdict is text this
    office stands behind, so it should be heard from the surface that serves it instead of proxied
    through a review console. Nothing is synthesised until somebody opens it.
    """
    from urllib.parse import quote, urlencode
    base = (endpoint or "").strip().rstrip("/")
    if not base:
        return "<div class='sv-warn'>no endpoint — point it at a host serving <code>/voicey</code></div>"
    line = " ".join(str(text or "").split())
    over = len(line) > VOAICE_TEXT_CAP
    if over:
        line = line[:VOAICE_TEXT_CAP].rsplit(" ", 1)[0] + "…"
    q: Dict[str, str] = {}
    if line:
        q["text"] = line
    if (persona or "").strip():
        q["persona"] = persona.strip()
    if (voice or "").strip():
        q["voice"] = voice.strip()
    url = base + ("?" + urlencode(q, quote_via=quote) if q else "")
    lane = ("the <b>pre-rendered</b> lane — this persona's own first line, a file read and no synthesis"
            if not line else
            f"the <b>synthesised</b> lane — {len(line)} of {VOAICE_TEXT_CAP} characters"
            + (" (the line was trimmed to the cap on a word boundary)" if over else ""))
    return (f"<div class='mx-card'><div class='sv-kv'>"
            f"<span>lane</span><span>{lane}</span>"
            f"<span>voice</span><span><code>{q.get('voice', '(the persona\\'s own preset)')}</code></span>"
            f"<span>persona</span><span><code>{q.get('persona', '(none — the host decides)')}</code></span>"
            f"<span>bounds</span><span>240 characters · 20 a minute · one slot at a time</span>"
            f"<span>producer</span><span>named in the <code>X-Voaice-Backend</code> response header, so what "
            f"you hear is attributable</span>"
            f"</div><p style='margin:10px 0 0'><a href='{url}' target='_blank' rel='noopener'>"
            f"open the audition →</a></p>"
            f"<p class='mx-sub' style='margin:6px 0 0;word-break:break-all'><code>{url}</code></p></div>")


# ── the office ────────────────────────────────────────────────────────────────
def savante_root() -> Optional[Path]:
    """Savante's canon: `SAVANTE_ROOT`, else this file's own directory, else `~/savante`."""
    here = Path(__file__).resolve().parent
    env = os.environ.get("SAVANTE_ROOT")
    for p in ([Path(env)] if env else []) + [here, Path.home() / "savante"]:
        if p.is_dir() and (p / "savante.persona").is_file():
            return p
    return None


def office() -> Dict[str, Any]:
    """The charter, read from the persona. Never paraphrased here — the file is the authority."""
    root = savante_root()
    if root is None:
        return {"error": "no savante checkout found — set SAVANTE_ROOT to one"}
    try:
        p = json.loads((root / "savante.persona").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"error": f"savante.persona unreadable: {str(e)[:200]}"}
    card: Dict[str, Any] = {}
    try:
        card = json.loads((root / "savante.agentcard.json").read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"name": p.get("name"), "kind": p.get("kind"), "source": p.get("source"),
            "mantra": p.get("mantra"), "oath": p.get("oath"),
            "beliefs": [b.get("belief") for b in (p.get("bdi") or {}).get("beliefs", [])],
            "verdicts": VERDICTS,
            "mint_status": (card.get("savante") or {}).get("status", "unknown"),
            "card_type": card.get("type"),
            "tool_allowlist": "Read, Grep, Glob, Bash — no Edit, no Write, no Agent",
            "root": str(root)}


def office_html() -> str:
    o = office()
    if o.get("error"):
        return f"<div class='sv-warn'>{o['error']}</div>"
    beliefs = "".join(f"<li>{b}</li>" for b in o["beliefs"][:8])
    return (f"<div class='mx-card'><div class='sv-mantra'>{o['mantra']}</div>"
            f"<div class='sv-oath'>{o['oath']}</div>"
            f"<div class='sv-kv'><span>office</span><span>{o['name']} · {o['kind']} · <code>{o['source']}</code></span>"
            f"<span>authority</span><span>{o['tool_allowlist']}</span>"
            f"<span>verdicts</span><span>{' · '.join(o['verdicts'])}</span>"
            f"<span>card</span><span>{o['card_type'] or '—'}</span>"
            f"<span>mint status</span><span><b>{o['mint_status']}</b> — nothing here mints anything</span>"
            f"<span>canon</span><span><code>{o['root']}</code></span></div>"
            f"<ul class='sv-beliefs'>{beliefs}</ul></div>")


# ── evidence: verification that actually runs ─────────────────────────────────
def run_evidence(cmd: str, cwd: str = "", timeout: float = 180.0) -> Dict[str, Any]:
    """Run one read-only verification command and report what actually happened.

    Refusal is part of the contract: a verb outside the allowlist, or any verb on the forbidden list,
    is declined with its reason rather than run. Savante executes verifications; it does not act.
    """
    cmd = (cmd or "").strip()
    if not cmd:
        return {"ok": False, "refused": "empty command"}
    try:
        parts = shlex.split(cmd)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "refused": f"unparsable: {str(e)[:120]}"}
    verb = Path(parts[0]).name
    if verb in FORBIDDEN or any(Path(t).name in FORBIDDEN for t in parts[:2]):
        return {"ok": False, "refused": f"'{verb}' can change state — the office is read-only by charter"}
    if verb not in SAFE_VERBS:
        return {"ok": False, "refused": f"'{verb}' is not on the verification allowlist",
                "allowed": sorted(SAFE_VERBS)}
    if any(t in (">", ">>", "|", ";", "&&", "&") for t in parts):
        return {"ok": False, "refused": "no redirection or chaining — one command, one result"}
    where = Path(cwd).expanduser() if cwd else (savante_root() or Path.cwd())
    t0 = time.monotonic()
    try:
        r = subprocess.run(parts, cwd=str(where), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "refused": f"timed out after {timeout:g}s", "cmd": cmd}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "refused": f"{type(e).__name__}: {str(e)[:160]}", "cmd": cmd}
    return {"ok": r.returncode == 0, "cmd": cmd, "cwd": str(where), "exit": r.returncode,
            "seconds": round(time.monotonic() - t0, 2),
            "stdout": (r.stdout or "")[-8000:], "stderr": (r.stderr or "")[-2000:],
            "note": "actual result; no interpretation added"}


# ── findings and the verdict contract ─────────────────────────────────────────
def add_finding(rows: Optional[List[List[str]]], claim: str, citation: str,
                state: str, deciding: str) -> List[List[str]]:
    """One finding: the claim, the file:line that carries it, known or not yet known, and — when it is
    not yet known — the experiment that would decide it. A finding without either is not a finding."""
    rows = [list(r) for r in (rows or []) if any(str(c).strip() for c in r)]
    claim = (claim or "").strip()
    if not claim:
        return rows
    state = state if state in ("known", "not yet known") else "not yet known"
    if state == "not yet known" and not (deciding or "").strip():
        deciding = "UNSTATED — a not-yet-known without a deciding experiment is an apology, not a finding"
    rows.append([claim, (citation or "").strip() or "—", state, (deciding or "").strip() or "—"])
    return rows


def render_verdict(rows: Optional[List[List[str]]], verdict: str, rationale: str,
                   conditions: str, risks: str, target: str) -> str:
    """The five-field contract, and the one refusal the oath requires."""
    rows = [r for r in (rows or []) if any(str(c).strip() for c in r)]
    verdict = verdict if verdict in VERDICTS else "DEFER"
    if verdict.startswith("APPROVE") and not rows:
        return ("## REFUSED BY THE CONTRACT\n\n"
                f"`{verdict}` was requested with **no findings recorded**. The oath reads *I will render "
                "verdicts only from evidence I have read, and I will read before I rule.* Record at least "
                "one finding with its citation, or render REJECT or DEFER — either of which may stand on an "
                "absence of evidence, while an approval may not.")
    known = [r for r in rows if r[2] == "known"]
    unknown = [r for r in rows if r[2] != "known"]
    out = [f"# Savante — review of {target or 'the stated claim'}", "",
           f"*Rendered in the five-field contract. {len(known)} finding(s) verified, "
           f"{len(unknown)} not yet known. Engine recorded, never pinned.*", "", "## FINDINGS", ""]
    for i, r in enumerate(rows, 1):
        out += [f"{i}. **{r[0]}**", f"   - evidence: `{r[1]}`", f"   - state: **{r[2]}**"]
        if r[2] != "known":
            out.append(f"   - deciding experiment: {r[3]}")
        out.append("")
    out += [f"## VERDICT: {verdict}", "", "## RATIONALE", "",
            (rationale or "").strip() or "_not stated_", "", "## CONDITIONS", ""]
    conds = [c.strip() for c in (conditions or "").splitlines() if c.strip()]
    out += ([f"{i}. {c}" for i, c in enumerate(conds, 1)] or
            ["_none — a verdict with no conditions is a verdict that needs none_"])
    out += ["", "## RISKS WATCHED", "", (risks or "").strip() or "_none stated_", "", "---", "",
            "*Savante Knows. Knowledge Is What Survives Verification; Nothing Else Counts.*"]
    return "\n".join(out)


# ── integrity: recompute the bundle, do not trust it ──────────────────────────
def cid_v1_raw(data: bytes) -> str:
    """CIDv1, raw codec, sha2-256, base32-lower — the construction mindX publishes THOTs under."""
    digest = hashlib.sha256(data).digest()
    raw = bytes([0x01, 0x55, 0x12, len(digest)]) + digest
    alpha = "abcdefghijklmnopqrstuvwxyz234567"
    bits = acc = 0
    out: List[str] = []
    for byte in raw:
        acc = (acc << 8) | byte
        bits += 8
        while bits >= 5:
            bits -= 5
            out.append(alpha[(acc >> bits) & 31])
    if bits:
        out.append(alpha[(acc << (5 - bits)) & 31])
    return "b" + "".join(out)


def integrity() -> Tuple[List[List[Any]], str]:
    """Recompute every committed artefact from the bytes on disk and compare with the ledger."""
    root = savante_root()
    if root is None:
        return [], "<div class='sv-warn'>no savante checkout found — set SAVANTE_ROOT</div>"
    try:
        ledger = json.loads((root / "savante.commitments.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [], f"<div class='sv-warn'>commitments unreadable: {str(e)[:160]}</div>"
    flat: Dict[str, str] = {}
    arts = ledger.get("artifacts") or {}
    for k, v in (arts.items() if isinstance(arts, dict) else []):
        if isinstance(v, dict):
            sha = str(v.get("sha256") or v.get("digest") or "").lower().replace("0x", "")
            if sha:
                flat[str(v.get("path") or k)] = sha
    rows: List[List[Any]] = []
    agree = disagree = unknown = 0
    for rel in BUNDLE:
        p = root / rel
        if not p.is_file():
            rows.append([rel, "absent", "—", "—", "file not in this checkout"])
            unknown += 1
            continue
        data = p.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        want = flat.get(rel) or flat.get(str(p)) or ""
        if not want:
            state, unknown = "not ledgered", unknown + 1
        elif want == sha:
            state, agree = "agrees", agree + 1
        else:
            state, disagree = "DISAGREES", disagree + 1
        rows.append([rel, f"{len(data)} B", sha[:16] + "…", cid_v1_raw(data)[:20] + "…", state])
    gen = ledger.get("generated_from") or {}
    head = str(gen.get("repo_head_commit") or "")
    diff = gen.get("components_differing_from_head") or []
    note = (f"<div class='sv-kv'><span>ledger head</span><span><code>{head[:12] or '—'}</code>"
            + (f" · <b>{len(diff)} component(s) differ from that commit</b> — these are a working tree's "
               "digests, not a commit's" if diff else " · ledger matches its commit") + "</span>"
            f"<span>recomputed</span><span>{agree} agree · <b>{disagree} disagree</b> · {unknown} unledgered</span>"
            f"<span>meaning</span><span>" + ("the charter's integrity is provable from these bytes"
              if disagree == 0 else "a committed artefact no longer matches its digest — read it before trusting it")
            + "</span></div>")
    return rows, note


# ── the look: the house palette, inlined ──────────────────────────────────────
CSS = """
:root, .gradio-container { --mx-bg:#0a0a12; --mx-panel:#11131c; --mx-line:rgba(120,140,200,.18); --mx-text:#dbe4ff;
  --mx-text2:#9aa6c8; --mx-accent:#58a6ff; --mx-green:#56d364; --mx-amber:#e3b341; --mx-red:#f85149; }
.gradio-container { background: radial-gradient(circle at 50% -10%, #161a2e 0%, var(--mx-bg) 60%) !important;
  color: var(--mx-text) !important; font-family: ui-monospace, SFMono-Regular, Menlo, monospace !important; }
.mx-card { background: var(--mx-panel); border:1px solid var(--mx-line); border-radius:12px; padding:12px 14px; }
.sv-mantra { font-size:1.05rem; font-weight:600; letter-spacing:.2px; margin-bottom:6px; color:var(--mx-amber); }
.sv-oath { font-style:italic; opacity:.85; margin-bottom:10px; line-height:1.5; }
.sv-kv { display:grid; grid-template-columns:max-content 1fr; gap:4px 14px; font-size:.92rem; }
.sv-kv span:nth-child(odd) { opacity:.6; white-space:nowrap; }
.sv-beliefs { margin:10px 0 0 0; padding-left:18px; font-size:.9rem; opacity:.9; line-height:1.6; }
.sv-warn { border:1px solid #6b4a1f; background:#1d1710; border-radius:10px; padding:10px 12px; }
.mx-pills span.pill { display:inline-block; border:1px solid var(--mx-line); border-radius:999px; padding:3px 11px;
  font-size:.78rem; color:var(--mx-text2); background:rgba(17,19,28,.8); margin:2px 6px 2px 0; }
.mx-pills span.pill.ok { color:var(--mx-green); border-color:rgba(86,211,100,.4); }
.mx-pills span.pill.warn { color:var(--mx-amber); border-color:rgba(227,179,65,.4); }
.mx-pills span.pill.bad { color:var(--mx-red); border-color:rgba(248,81,73,.4); }
footer { display:none !important; }
/* Gradio 6 tables and inline code ignore the Base tokens — measured white rows, invisible chips */
.gradio-container { --table-even-background-fill:#121521; --table-odd-background-fill:#0f1119;
  --table-border-color:rgba(120,140,200,.18); --table-text-color:#dbe4ff; --code-background-fill:rgba(88,166,255,.10); }
.gradio-container table, .gradio-container .table-wrap, .gradio-container [data-testid="dataframe"] { background:#11131c !important; }
.gradio-container th, .gradio-container thead td { background:#161a28 !important; color:#9aa6c8 !important; }
.gradio-container td { background:#0f1119 !important; color:#dbe4ff !important; }
.gradio-container tbody tr:nth-child(even) td { background:#121521 !important; }
.gradio-container code, .gradio-container .prose code { background:rgba(88,166,255,.10) !important; color:#dbe4ff !important;
  padding:1px 5px; border-radius:4px; border:none !important; }
"""


def pills(items) -> str:
    return '<div class="mx-pills">' + "".join(f'<span class="pill {c}">{t}</span>' for t, c in items) + "</div>"


def _theme():
    """The house palette as a Gradio theme. Token names differ between majors, so pass only what
    `.set()` actually accepts — read the signature, never pin a version."""
    import inspect

    import gradio as gr
    want = {"body_background_fill": "#0a0a12", "body_background_fill_dark": "#0a0a12",
            "block_background_fill": "#11131c", "block_background_fill_dark": "#11131c",
            "block_border_color": "rgba(120,140,200,.18)", "body_text_color": "#dbe4ff",
            "body_text_color_dark": "#dbe4ff", "block_title_text_color": "#9aa6c8",
            "button_primary_background_fill": "#1b2233", "button_primary_text_color": "#e3b341",
            "input_background_fill": "#0c0e16",
            "table_even_background_fill": "#121521", "table_odd_background_fill": "#0f1119",
            "table_text_color": "#dbe4ff", "code_background_fill": "rgba(88,166,255,.10)"}
    try:
        base = gr.themes.Base(primary_hue="yellow", secondary_hue="blue", neutral_hue="slate")
        ok = set(inspect.signature(gr.themes.Base.set).parameters)
        return base.set(**{k: v for k, v in want.items() if k in ok})
    except Exception:
        return gr.themes.Base()


def status_pills() -> str:
    o = office()
    root_ok = not o.get("error")
    rows, _ = integrity() if root_ok else ([], "")
    disagree = sum(1 for r in rows if r[-1] == "DISAGREES")
    return pills([
        (f"savante {VERSION}", ""),
        ("canon found" if root_ok else "no canon — set SAVANTE_ROOT", "ok" if root_ok else "bad"),
        (f"mint: {o.get('mint_status', 'unknown')}", "warn"),
        ("read-only charter", "ok"),
        (f"bundle: {len(rows) - disagree}/{len(rows)} agree" if rows else "bundle unchecked",
         "ok" if rows and not disagree else ("bad" if disagree else "warn")),
        ("kimi key present" if kimi_key() else "kimi dormant", "ok" if kimi_key() else ""),
        ("paid lanes not armed" if os.environ.get("MINDX_HF_ALLOW_PAID") != "1" else "PAID ARMED",
         "" if os.environ.get("MINDX_HF_ALLOW_PAID") != "1" else "warn"),
    ])


def build():
    """The six rooms. gradio is imported here so this module can be read, hashed and audited without it."""
    import inspect

    import gradio as gr

    blocks_takes_theme = "theme" in inspect.signature(gr.Blocks.__init__).parameters
    copy_kw = ({"show_copy_button": True}
               if "show_copy_button" in inspect.signature(gr.Textbox.__init__).parameters else {})
    bk = {"theme": _theme(), "css": CSS} if blocks_takes_theme else {}

    with gr.Blocks(title="Savante — the oversight office", **bk) as demo:
        gr.Markdown("# Savante\n**savante_sagi · Chairman of the mindX DAIO · the prototype sAGI.** "
                    "The structural substrate: rarely intervenes, always watching. Read-only by charter — "
                    "this surface reviews, verifies and renders; it never edits what it audits.")
        pill_row = gr.HTML(status_pills())

        with gr.Tabs():
            with gr.Tab("The Office"):
                off = gr.HTML(office_html())
                gr.Button("re-read the charter").click(lambda: (office_html(), status_pills()), None, [off, pill_row])
                gr.Markdown("*Nothing here mints anything.* `iNFT.md` renders **VERDICT: DEFER** on binding "
                            "this office to a token, and minting, listing, vault binding and registry "
                            "registration are factory steps awaiting the operator's signature. A button for "
                            "them would claim an authority the charter does not hold.")

            with gr.Tab("Evidence"):
                gr.Markdown("**Verification, executed.** A linter checks rules; Savante checks claims — run "
                            "the tests and report the count, read the git state and report the drift, grep for "
                            "the capability a document asserts. Read-only verbs only, and a refusal states its reason.")
                with gr.Row():
                    ev_cmd = gr.Textbox(value="git log --oneline -5", label="verification command", scale=3)
                    ev_cwd = gr.Textbox(value="", label="working directory (blank = the canon)", scale=2)
                    ev_go = gr.Button("run", variant="primary", scale=1)
                ev_out = gr.Code(label="actual result", language="json", interactive=False)
                ev_go.click(lambda c, w: json.dumps(run_evidence(c, w), indent=1), [ev_cmd, ev_cwd], [ev_out])

            with gr.Tab("Verdict"):
                gr.Markdown("**The fixed contract.** Findings with citations, then one of four verdicts, a "
                            "rationale, numbered conditions each independently verifiable by someone who is "
                            "not the officer, and the risks being watched.")
                target = gr.Textbox(value="", label="what is under review")
                with gr.Row():
                    f_claim = gr.Textbox(value="", label="claim", scale=3)
                    f_cite = gr.Textbox(value="", label="evidence (file:line, tx, test)", scale=2)
                    f_state = gr.Radio(["known", "not yet known"], value="known", label="state", scale=1)
                    f_dec = gr.Textbox(value="", label="deciding experiment (if unknown)", scale=2)
                    f_add = gr.Button("record", scale=1)
                findings = gr.Dataframe(headers=["claim", "evidence", "state", "deciding experiment"],
                                        value=[], interactive=True, wrap=True, label="findings")
                v_pick = gr.Radio(VERDICTS, value="DEFER", label="verdict")
                with gr.Row():
                    v_rat = gr.Textbox(value="", lines=3, label="rationale")
                    v_cond = gr.Textbox(value="", lines=3, label="conditions (one per line)")
                    v_risk = gr.Textbox(value="", lines=3, label="risks watched")
                v_go = gr.Button("render the verdict", variant="primary")
                v_out = gr.Markdown("")
                f_add.click(add_finding, [findings, f_claim, f_cite, f_state, f_dec], [findings])
                v_go.click(render_verdict, [findings, v_pick, v_rat, v_cond, v_risk, target], [v_out])

            with gr.Tab("Integrity"):
                gr.Markdown("**Recompute, do not trust.** Every committed artefact is hashed from the bytes on "
                            "disk and compared with the ledger. This is what a holder receives: the ability to "
                            "prove, without trusting the author, that DEFER is still in the vocabulary.")
                i_note = gr.HTML("")
                i_tbl = gr.Dataframe(headers=["artefact", "size", "sha256", "CIDv1 (raw)", "ledger"],
                                     value=[], interactive=False, wrap=True)
                i_go = gr.Button("recompute the bundle", variant="primary")
                i_go.click(lambda: integrity()[::-1], None, [i_note, i_tbl])
                demo.load(lambda: integrity()[::-1], None, [i_note, i_tbl])

            with gr.Tab("Rungs · Qwen3"):
                gr.Markdown("**The ladder, as plan only.** The standing baseline is a 135M actor trained on "
                            "2 vCPU — a proven result, not a budget hope, and a proposal is graded against it. "
                            "Below are the Qwen3 rungs above it. **Nothing on this tab can spend anything:** a "
                            "rented lane needs the operator's flag on the node *and* the per-generation ceiling "
                            "to hold, and this surface has neither.")
                gr.Dataframe(value=rung_rows(), interactive=False, wrap=True,
                             headers=["rung", "params", "lane", "hardware", "VRAM", "cost", "state", "why"],
                             label="Qwen3 8B and 27B")
                gr.HTML(rung_note())
                gr.Markdown("Reading the rows: **8B** is the next step from the tiny actor and stays CPU-first "
                            "by doctrine, because CPU is standing capacity while GPU is episodic. **27B** is the "
                            "mid-grade and is GPU-only — an 80 GB A100 or a 96 GB RTX Pro, about $1.90 for a "
                            "45-minute run, which sits *at* the ceiling rather than under it. The **FP8** 27B "
                            "fits a cheaper 48 GB card at 30.8 GB, but base training on FP8 needs a dequantised "
                            "path and is marked experimental rather than ready. Every duration is an assumption "
                            "until a settled job replaces it with measured minutes.")

            with gr.Tab("Kimi"):
                gr.Markdown("**Provider configuration.** Kimi is Moonshot AI's model family, served over an "
                            "OpenAI-compatible API. This tab configures and checks it. The office's standing is "
                            "unchanged by its presence: **a model's prose is a draft, never a finding** — a "
                            "verdict comes from evidence that was read.")
                k_note = gr.HTML(kimi_status())
                with gr.Row():
                    k_base = gr.Dropdown(choices=KIMI["bases"], value=KIMI["bases"][0], allow_custom_value=True,
                                         label="base URL", scale=2)
                    k_model = gr.Textbox(value=KIMI["default_model"], label="model id", scale=2, **copy_kw)
                    k_list = gr.Button("list models", scale=1)
                    k_refresh = gr.Button("re-check key", scale=1)
                gr.Markdown(f"*{KIMI['note']}* **Model identifiers rot**, so the list endpoint is the authority "
                            "and the field stays editable — the same rule this house applies to every provider "
                            "roster. A 401 or 403 usually means the key belongs to the other host, since the "
                            "international and CN endpoints issue separately.")
                k_models = gr.Code(label="what the provider says it serves", language="json", interactive=False)
                with gr.Row():
                    k_sys = gr.Textbox(value="", lines=3, label="system", scale=2)
                    k_prompt = gr.Textbox(value="", lines=3, label="prompt", scale=3)
                with gr.Row():
                    k_temp = gr.Slider(0.0, 2.0, value=0.6, step=0.05, label="temperature")
                    k_max = gr.Slider(64, 8192, value=1024, step=64, label="max_tokens")
                    k_ask = gr.Button("ask (returns a DRAFT)", variant="primary")
                k_out = gr.Textbox(label="draft — not a finding, not a verdict", lines=12, interactive=False, **copy_kw)
                k_meta = gr.Code(label="meta", language="json", interactive=False)
                k_list.click(kimi_models, [k_base], [k_models])
                k_refresh.click(lambda: (kimi_status(), status_pills()), None, [k_note, pill_row])
                k_ask.click(kimi_ask, [k_base, k_model, k_sys, k_prompt, k_temp, k_max], [k_out, k_meta])

            with gr.Tab("Voice · voaice"):
                gr.Markdown("**The verdict, read aloud.** Adapted from the rage player on "
                            "`deltaverse.pythai.net/playdocs`, which speaks a line two ways and this tab "
                            "keeps both. **voaice** is a GET: omit the text and the server plays that "
                            "persona's own first **pre-rendered** line, which is why auditioning the cast is "
                            "free — ten voices cost ten file reads and no synthesis. Supply text and it is "
                            "synthesised instead, which is **bounded rather than refused**: a 240-character "
                            "cap, twenty a minute, one slot at a time. The **docsplayer** tier is the other "
                            "lane: the host renders the line, queues it, files it, and the player plays the "
                            "file — which is how a long passage gets spoken at all.")
                with gr.Row():
                    vo_url = gr.Textbox(value="https://deltaverse.pythai.net/voicey", label="voaice endpoint", scale=2)
                    vo_voice = gr.Dropdown(choices=VOAICE_VOICES, value="sagi", allow_custom_value=True,
                                           label="voice", scale=1)
                    vo_persona = gr.Textbox(value="savante", label="persona", scale=1)
                vo_text = gr.Textbox(value="", lines=3, label="line (blank = that persona's own first line, pre-rendered)")
                with gr.Row():
                    vo_link = gr.Button("build the audition link", variant="primary")
                    vo_from_verdict = gr.Button("speak the verdict's first line")
                vo_out = gr.HTML("")
                gr.Markdown(f"*Voice ids verified from `voicey.js`:* `{'` · `'.join(VOAICE_VOICES)}`, plus "
                            "`custom:<16 hex>` for a studio recipe composed in playdocs. `sagi` is the default "
                            "here because it is the office's own voice. Every response names its producer in "
                            "`X-Voaice-Backend`, so what you hear is attributable.\n\n"
                            "**Why a link and not a player:** this tab builds the request rather than fetching "
                            "it, because the endpoint lives on another origin and a verdict is text the office "
                            "stands behind — it should be heard from the surface that serves it, not proxied "
                            "through a review console. Nothing is synthesised until you open the link.")
                vo_link.click(voaice_link, [vo_url, vo_text, vo_persona, vo_voice], [vo_out])
                vo_from_verdict.click(lambda u, p, v, md: voaice_link(u, _first_line(md), p, v),
                                      [vo_url, vo_persona, vo_voice, v_out], [vo_out])

        gr.HTML("<div class='mx-sub' style='opacity:.6;margin-top:12px;font-size:.9rem'>Savante Knows. "
                "Knowledge Is What Survives Verification; Nothing Else Counts. · "
                "canon: github.com/cryptoAGI/savante · look: the mindXhfgradio Space</div>")

    demo.mx_launch = {} if blocks_takes_theme else {"theme": _theme(), "css": CSS}
    return demo


def main(host: str = "127.0.0.1", port: int = 7863, share: bool = False) -> None:
    demo = build()
    demo.queue(default_concurrency_limit=2).launch(server_name=host, server_port=port, share=share,
                                                   **getattr(demo, "mx_launch", {}))


if __name__ == "__main__":
    main()
