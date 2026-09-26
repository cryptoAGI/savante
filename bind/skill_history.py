#!/usr/bin/env python3
"""bind/skill_history.py — .memory -> .history -> .skill, for the sagi skill (improve.skill).

  .claude/skills/sagi/.memory    append-only JSONL: every interaction with the skill as it happened, the engine's
                                 own counts included. Never edited, never reordered; a wrong line is corrected by a
                                 later line, not by rewriting.
  .claude/skills/sagi/.history   DERIVED from .memory by this program, byte-for-byte reproducible: the interactions
                                 that pass the three checks, numbered, each with the one improvement it motivated.
  .claude/skills/sagi/SKILL.md   the .skill: changed only by improvements that .history names.

The three checks (an interaction that fails any of them is kept in .memory and does not count):
  1. single delivery   deliveries == 1 — one answer, no retries, no regeneration
  2. minimum necessary the token limit was set once, the engine's own counts are present, the answer ended on its
                       own (finish == "stop", not "length"), and completion_tokens <= limit; the unused headroom
                       (limit - completion_tokens) is recorded so the next limit can be smaller
  3. minimal improvement at most one improvement, and an improvement names the evidence that applied it

improve.skill version: n verified interactions -> n//1000 . (n%1000)//100 . n%100
  (1 -> 0.0.1, 99 -> 0.0.99, 100 -> 0.1.0, 999 -> 0.9.99, 1000 -> 1.0.0). 1.0.0 is earned at 1000.

  python3 bind/skill_history.py            # write .history from .memory, print the version
  python3 bind/skill_history.py --check    # exit 1 if .history is not exactly what .memory projects to
stdlib only, no network, no wall clock: two runs over the same .memory produce the same bytes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "sagi"
MEMORY, HISTORY = SKILL / ".memory", SKILL / ".history"
ROAD = 1000


def version(n: int) -> str:
    return f"{n // 1000}.{(n % 1000) // 100}.{n % 100}"


def checks(m: dict) -> list:
    """The reasons an interaction does not count; empty when it passes."""
    why = []
    if m.get("deliveries") != 1:
        why.append(f"single delivery: deliveries is {m.get('deliveries')!r}, not 1")
    u, lim = m.get("usage") or {}, m.get("limit")
    ct = u.get("completion_tokens")
    if not isinstance(lim, int) or lim < 1:
        why.append("minimum necessary: no token limit recorded")
    if not isinstance(ct, int):
        why.append("minimum necessary: no completion_tokens counted by the engine")
    elif isinstance(lim, int) and ct > lim:
        why.append(f"minimum necessary: {ct} completion tokens exceed the limit {lim}")
    if m.get("finish") != "stop":
        why.append(f"minimum necessary: finish is {m.get('finish')!r}, not 'stop' (the answer was cut or failed)")
    imp = m.get("improvement")
    if imp is not None and (not isinstance(imp, dict) or not imp.get("change") or not imp.get("evidence")):
        why.append("minimal improvement: an improvement must name one change and the evidence that applied it")
    return why


def project(lines: list) -> tuple:
    verified, refused = [], []
    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue
        m = json.loads(line)
        why = checks(m)
        if why:
            refused.append({"memory_line": i, "id": m.get("id"), "why": why})
            continue
        n = len(verified) + 1
        u = m["usage"]
        verified.append({"n": n, "version": version(n), "memory_line": i, "id": m.get("id"), "date": m.get("date"),
                         "carrier": m.get("carrier"), "question": m.get("question"), "answer": m.get("answer"),
                         "limit": m["limit"], "completion_tokens": u["completion_tokens"],
                         "prompt_tokens": u.get("prompt_tokens"), "headroom": m["limit"] - u["completion_tokens"],
                         "improvement": m.get("improvement")})
    return verified, refused


def render(verified: list, refused: list) -> bytes:
    n = len(verified)
    head = {"kind": "sagi.skill_history/1", "derived_from": ".claude/skills/sagi/.memory",
            "by": "bind/skill_history.py", "improve_skill_version": version(n), "verified": n, "road": ROAD,
            "refused": refused}
    out = [json.dumps(head, ensure_ascii=False, sort_keys=True)]
    out += [json.dumps(v, ensure_ascii=False, sort_keys=True) for v in verified]
    return ("\n".join(out) + "\n").encode("utf-8")


def main() -> int:
    lines = MEMORY.read_text(encoding="utf-8").splitlines() if MEMORY.exists() else []
    verified, refused = project(lines)
    data = render(verified, refused)
    if "--check" in sys.argv:
        ok = HISTORY.exists() and HISTORY.read_bytes() == data
        print(("KNOWN   .history is the projection of .memory" if ok else
               "FAIL    .history differs from what .memory projects to — rerun bind/skill_history.py"))
        print(f"improve.skill v{version(len(verified))} — {len(verified)} of {ROAD} verified interactions, {len(refused)} refused")
        return 0 if ok else 1
    HISTORY.write_bytes(data)
    print(f"wrote {HISTORY.relative_to(ROOT)} — improve.skill v{version(len(verified))}: "
          f"{len(verified)} of {ROAD} verified interactions, {len(refused)} refused")
    for r in refused:
        print(f"  refused memory line {r['memory_line']}: {'; '.join(r['why'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
