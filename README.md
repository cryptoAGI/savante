# Savante

**The prototype sAGI — an objective-truth review agent for Claude Code.**

> *Savante knows. Knowledge is what survives verification; nothing else counts.*

Savante is a board-level reviewer packaged as two plain-text files. Installed
into any repository, it renders evidence-backed verdicts on claims — *is this
production-ready? does the code do what the docs assert? should this merge?* —
by actually verifying them: running the tests, reading the git state, and
searching for the capability a document claims. It is read-only by
construction, and it never approves what it has not read.

Savante originates as `savante_sagi`, Chairman of the
[mindX](https://github.com/AgenticPlace/mindX) DAIO, and serves as the
prototype for **sAGI**: a discipline of verification-or-unknown, honest
labeling, and bounded authority, run on whatever model carries the session.

---

## How it works

Savante consists of two functional artifacts:

| Artifact | Role |
|---|---|
| `.claude/agents/savante.md` | The **charter** — a Claude Code subagent definition. Its frontmatter restricts the agent to read-only tools (`Read, Grep, Glob, Bash`); its body is the complete system prompt: identity, epistemology, standing constraints, and verdict format. |
| `.claude/skills/sagi/SKILL.md` | The **`/sagi` skill** — the invocation surface. It launches the savante agent, mandates verification over inference, and defines a fallback for sessions where the agent type is not yet registered. |

The epistemology is fixed: a claim is **known** when it is verifiable against
evidence — code that exists, a test that passes, a ledger entry, a mainnet
transaction — and **unknown** otherwise. Anything unverifiable is reported as
*not yet known*, together with the experiment that would decide it.

## Quick start

**Install** into a repository (or `~/.claude/` for all projects):

```bash
git clone https://github.com/cryptoAGI/savante
cp    savante/.claude/agents/savante.md  <your-repo>/.claude/agents/
cp -r savante/.claude/skills/sagi        <your-repo>/.claude/skills/
```

The agent type registers at the next Claude Code session start; the `/sagi`
skill's fallback path works immediately.

**Invoke** inside Claude Code:

```
/sagi review the payment router changes
have savante review <target> production readiness
render a verdict on <claim>
```

**Adapt** by editing one section of the charter — *"Canon you measure
against"* — to point at your repository's own doctrine documents. The
epistemology, verdict contract, and read-only tooling are the invariant core.

## The verdict contract

Every review returns a fixed, machine-parseable structure:

```
FINDINGS        evidence per load-bearing claim (file:line), plus
                "not yet known" entries, each naming its deciding experiment
VERDICT:        APPROVE | APPROVE_WITH_CONDITIONS | REJECT | DEFER
RATIONALE:      2–5 sentences citing the deciding constraint
CONDITIONS:     numbered; each independently verifiable
RISKS WATCHED:  the risks Savante continues to monitor
```

`DEFER` is reserved for decisions that require the operator's signature
rather than gatherable evidence — a statement about jurisdiction, not a
failure. The fixed shape makes Savante usable as a CI merge gate; see
[usage.md](usage.md) for the GitHub Actions recipe and
[technical.md](technical.md) for the wiring details.

## Service modes

| Mode | Mechanism |
|---|---|
| Interactive | `/sagi` or "have savante review …" in a Claude Code session |
| CI gate | Headless `claude -p` in a pull-request workflow; grep the verdict line |
| API endpoint | Charter as system prompt via the Claude Agent SDK, read-only tool loop |
| Scheduled audit | Cron'd headless review of the period's changes |

Duplication is the deployment model: copying the two `.claude/` files
replicates the service into any repository, organization, or pipeline. See
[SAVANTE_AS_A_SERVICE.md](SAVANTE_AS_A_SERVICE.md).

## Documentation

| Document | Contents |
|---|---|
| [Savante.md](Savante.md) | Written by Savante itself — the office in its own voice |
| [savante.md](savante.md) | The full charter, mirrored at top level for reading |
| [sAGI.md](sAGI.md) | The sAGI definition: three laws, full skill text |
| [MANIFESTO.md](MANIFESTO.md) | The mindX Manifesto adapted for Savante — the knowledge economy as the evolution from the information age |
| [explanation.md](explanation.md) | Design rationale — why read-only, why a fixed contract, why no model pinning |
| [technical.md](technical.md) | File formats, harness mechanics, verdict contract as API, service wiring |
| [usage.md](usage.md) | Install, invoke, adapt, CI gate, scheduled audit, reading verdicts |
| [SAVANTE_AS_A_SERVICE.md](SAVANTE_AS_A_SERVICE.md) | How sAGI works with Claude; duplication paths |

## Design principles

1. **Verification or unknown.** Nothing enters a verdict by inference; what
   could not be verified is labeled *not yet known* with its deciding
   experiment.
2. **Honest labeling.** A system that states its limitations truthfully can
   pass review; the same system overstating them cannot. The claim, not the
   capability, is what fails.
3. **Bounded authority.** Read-only enforced by the harness, not by prompt;
   `DEFER` at the edge of jurisdiction.
4. **Model portability.** No model pinning — the charter must survive an
   engine swap, or it was never a discipline.
5. **Plain-text everything.** The service is two markdown files: diffable,
   auditable, forkable, installable with `cp`.

## The measured economy

Savante's doctrine is instrumented on-chain within the PYTHAI constellation:
**SCIEN·TIFIC** tokenizes measured accuracy (with chronos.oracle attesting
time-truth), **LUV** measures the value of attention via proof of gesture,
and **CP2048-QR** tiers security claims by evidence. Both tokens derive value
from being priceless — value creates price, never the reverse. Verified value
circulates bankon → mindx → agenticplace: identity proven, knowledge
delivered, exchange made. Details: [MANIFESTO.md](MANIFESTO.md).

## Provenance

Authored within the mindX Gödel-machine project (Project Chimaiera) by
[Professor Codephreak](https://github.com/Professor-Codephreak), software
engineer and platform architect of the PYTHAI constellation. First verdict
rendered 2026-07-26 — parsec-wallet production readiness:
APPROVE_WITH_CONDITIONS.

---

*Savante is read-only by charter. It renders verdicts; it does not edit code.*
