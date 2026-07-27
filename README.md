# SAVANTE — the prototype sAGI

**savante knows.**

Savante (`savante_sagi`) is the Chairman of the mindX DAIO — `core_command`,
alongside PYTHAI, SUNTSU, and RAGE — and the prototype for **sAGI**. Doctrine:
*the structural substrate — rarely intervenes, always watching.*

Its epistemology is scientific, not moral. **Science requires objective
truth**: a claim is *known* when it survives verification against evidence —
code that exists, a ledger entry, a measurement, a mainnet transaction, a
proof — and *unknown* otherwise. Savante holds findings, not opinions. When a
thing is not yet known, Savante states that as a fact and names the experiment
that would decide it.

## The measurement stack

The same discipline, instrumented on-chain — accuracy and attention are
measured quantities, never assertions:

| Axis | Instrument | Surface |
|---|---|---|
| Accuracy | **SCIEN·TIFIC** token (with **chronos.oracle** for time-truth) | scientific.pythai.net |
| Attention | **LUV** — value of attention via **proof of gesture** | luv.pythai.net |
| Security claims | **CP2048-QR** — mandatory honest labeling; Tier-Q only where a mainnet txn proves it | github.com/cypherpunk2048 |

That stack prices the agentic economy, circulating through three surfaces:
**bankon.pythai.net** (identity + WaaS) → **mindx.pythai.net** (intelligence +
knowledge-delivery) → **agenticplace.pythai.net** (marketspace).

## What is in this repository

Savante packaged as a drop-in [Claude Code](https://claude.com/claude-code)
reviewer:

```
.claude/agents/savante.md      — the charter: identity, canon, standing
                                 constraints, vision scope, verdict format
                                 (canonical, installable)
.claude/skills/sagi/SKILL.md   — /sagi: invoke the Savante review
                                 (canonical, installable)
```

Documentation — the full set:

| Document | What it holds |
|---|---|
| [Savante.md](Savante.md) | Written by Savante itself — the office in its own voice |
| [savante.md](savante.md) | The full charter, mirrored top-level for reading |
| [sAGI.md](sAGI.md) | What sAGI is — definition, three laws, full skill text |
| [MANIFESTO.md](MANIFESTO.md) | The mindX Manifesto adapted for Savante — knowledge economy, three pillars |
| [explanation.md](explanation.md) | Why it exists, why each design choice, knowledge vs. information age |
| [technical.md](technical.md) | File formats, harness mechanics, verdict contract as API, service wiring |
| [usage.md](usage.md) | Install, invoke, adapt, CI gate, scheduled audit, reading verdicts |
| [SAVANTE_AS_A_SERVICE.md](SAVANTE_AS_A_SERVICE.md) | Duplication paths — the charter as the whole service |

**Savante as a Service:** the charter is the whole service — duplicating the
two `.claude/` files replicates Savante into any repo, org, or CI pipeline.

## Install

Copy both paths into any repository (or into `~/.claude/` for all projects):

```bash
cp -r .claude/agents/savante.md      <your-repo>/.claude/agents/
cp -r .claude/skills/sagi            <your-repo>/.claude/skills/
```

Then, in Claude Code:

- `/sagi` — run a board-level review, or
- ask directly: *"have savante review \<target\>"*.

Savante is **read-only by charter** — it renders verdicts
(`APPROVE | APPROVE_WITH_CONDITIONS | REJECT | DEFER`) with file-and-line
evidence, verifiable conditions, and named risks. It never edits code, and it
never approves what it has not read.

## Verdict format

Every review produces:

- **FINDINGS** — evidence per claim; explicit *"not yet known"* entries with
  the deciding experiment
- **VERDICT** — APPROVE | APPROVE_WITH_CONDITIONS | REJECT | DEFER
- **RATIONALE** — board-minute style, citing the deciding constraint
- **CONDITIONS** — numbered, each independently verifiable
- **RISKS WATCHED** — what Savante keeps watching

## Lineage

Authored within the mindX Gödel-machine project (Project Chimaiera —
*"the logic that dreams, the monster that obeys"*) by Professor Codephreak,
software engineer and platform architect of the PYTHAI constellation.
First verdict rendered 2026-07-26: parsec-wallet production readiness →
APPROVE_WITH_CONDITIONS.

*Knowledge is what survives verification; nothing else counts.*
