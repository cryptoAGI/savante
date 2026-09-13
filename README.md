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

The `token` and `task` blocks of `savante.persona` were authored 2026-09-03.
The standards the token block cites are listed in `token.standards[]`, each
with the URL recorded as its `status_source` where one was fetched (the two
RFCs and the two non-standard entries carry `null`); the block records that
its author transcribed those statuses and did not itself fetch the pages
(`token.standards_note`).

## The persona as an iNFT

Savante's identity is also a mindX persona, `savante.persona` — its `.persona v1`
shape expanded from the founder template `mindX/mindx/godel/mindxtrain/personas/draiml.persona`
(recorded in the file's own `template` key) — and that file
now carries two additional top-level blocks: `token` — the whole iNFT surface
as inert data (standards, public metadata, grants, permanently-null binding
slots, rights, and the office's own verdict on minting) — and `task` — the
imprint battery a trainer grades it against. Around it sit the artifacts
below. None of them is part of the two-file install above: `cp` of the
charter and the skill conveys the office; these convey the office's ledger.

| Artifact | Role |
|---|---|
| `savante.persona` | The mindX persona — source of truth; carries the `token` (line 186) and `task` (line 565) blocks; its shape is expanded from the `draiml.persona` founder template (`template`, line 7). Mirrored byte-for-byte into mindX. |
| `iNFT.md` | The binding document, rendered in the five-field contract. Its verdict heading reads `## VERDICT: DEFER`. |
| `sAGI.agent` · `sAGI.model` | The two authored facets of mindX's six-facet blockchain-agent class (`agents/blockchain/facets.py:14-15,29`); `savante.persona` is the third authored facet, and the wallet/bankon/iNFT facets are written only by a mint pipeline. savante === sAGI.agent. |
| `savante.agentcard.json` | Derived public card — one document that is both an EIP-721 metadata instance and an ERC-8004 registration file. Built from `token.public_metadata` plus what the binder derives itself: the first-commit date read from `git log`, the digest pointers, and the mint status. Never hand-edited. |
| `savante.commitments.json` | Derived integrity ledger — raw-byte sha256 and CIDv1 per component, the doctrine root, the card digest, every binding slot null with its reason. The only place binding values ever live. |
| `bind/savante_bind.py` | The operator's binder — writes the two derived files. Savante audits it and never runs it. |
| `bind/savante_verify.py` | The holder's checker — recomputes every digest from raw bytes and prints the verdict block; exits 0 only on `VERDICT: APPROVE`. |
| `bind/verdict_record.schema.json` | JSON Schema for a ledger entry; `verdict` is a four-value enum, so a fifth verdict fails mechanically. |

Plain facts, kept on the front page because they are the ones a buyer would
most want elsewhere:

- **Nothing is minted** — not even a dry run. Evidence: no `savante.*` facet
  exists in mindX `agents/blockchain/` (the directory holds `abi_codec.py`,
  `agent_factory.py`, `algorand_verifier.py`, `contracts.py`, `facets.py`,
  `__init__.py`, `template.agent`, `template.model` and a `__pycache__/`;
  `ls`, 2026-09-03), and `/home/hacker/mindX/data/godel/thot/` does not exist
  (`ls`: No such file or directory, 2026-09-03). The ledger records
  `"mint": null`.
- **MIT licensed in this working tree — NOT YET PUBLISHED** (2026-09-11). An MIT
  `LICENSE`, © 2026 cryptoAGI, exists at the root of the working tree, matching
  the house licence of `voaice`. It is **untracked**: the published repository at
  github.com/cryptoAGI/savante is still at `ae15ca7`, whose tree contains no
  LICENSE, and GitHub reports the repo's licence as none. So a stranger who
  follows the only address this file prints finds no licence, and
  `iNFT.md` condition 1 is **closed locally and open publicly** until the commit
  is pushed. Deciding check, run against the URL rather than the disk:
  `gh api repos/cryptoAGI/savante/contents | grep LICENSE`.
  Note also the boundary the persona keeps: MIT governs the *copy* of these
  files; it is not a statement about what a token conveys, and
  `token.rights.conveyed_by_token` is still null with its reason
  (`savante.persona`, `token.rights`).
- **The binding document is `iNFT.md`, and its verdict is `DEFER`.** A mint
  is a visibility-or-publication decision and a treasury action — two of the
  office's own defer triggers (`savante.persona:136`) — so the decision is
  the operator's, not Savante's (`savante.persona:560-562`).

Verify the binding yourself, trusting nothing the author wrote:

```bash
git clone https://github.com/cryptoAGI/savante && cd savante
python3 bind/savante_verify.py .
python3 bind/savante_verify.py . | grep -qx 'VERDICT: APPROVE' && echo bound
```

Steps 1–5 need no network: raw-byte sha256 and CIDv1 of the persona, charter
and skill against the ledger; the preflight and the doctrine root over its
fifteen pointers; the charter allowlist exactly `Read, Grep, Glob, Bash`; and
the mindX mirror's md5. On a machine without mindX the mirror step is
reported as a condition, not a rejection (`bind/savante_verify.py:13-14`), so
expect `APPROVE_WITH_CONDITIONS` (exit 1) there and `APPROVE` (exit 0) on
the author's host. The `--onchain` step 6 has nothing to compare against
today: no registry address exists in this repository, and none is invented.

---

*Savante is read-only by charter. It renders verdicts; it does not edit code.*
