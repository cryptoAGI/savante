# Savante

<p align="center"><img src="gfx/Savante3.png" alt="Savante, the bust" width="320"></p>

**The prototype sAGI — an objective-truth review agent for Claude Code.**

**The public office.** The office's page is canon now, in [`space/`](space/), served as a static page (no server,
no compute of its own and no host key) at
[huggingface.co/spaces/PYTHAI/savante](https://huggingface.co/spaces/PYTHAI/savante) and
[Gregory-L/Savante](https://huggingface.co/spaces/Gregory-L/Savante), its first public page. The same canon, with the
sAGI engine, is mirrored to the model repository [PYTHAI/SAVANTE](https://huggingface.co/PYTHAI/SAVANTE), and the
skill's improvement loop is published as [PYTHAI/savante-loop](https://huggingface.co/datasets/PYTHAI/savante-loop).
Each mirror says which canon commit it carries in its own `MIRROR.json`. The page's `integrity()` hashes the bytes it
serves against `savante.commitments.json`. That agreement binds files to the ledger; it does not prove who wrote them,
and nothing there mints anything.

*The bust is Savante's artwork, named by the operator on 2026-09-16: `gfx/Savante3.png`, sha256
`30a59db4ce76dbea8b6a97c143a74996c3c1cd317e3af21f6a18757ae8c5a9a8`, recorded in the generation-7 ledger. It is
not pinned and nothing is minted, so the card's `image` is still null. Every image of Savante is indexed in
[gfx/README.md](gfx/README.md). The digests of this skill and every file that carries a proof are in
[PROOF.md](PROOF.md); check them with `sha256sum -c PROOF.sha256`.*

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

## The page: Faicey, PYTHAI and the rooms

`space/` is the office as a web page: plain ES modules, no build step, every string from a model, the Hub or a
file written with `textContent`. It comes in two editions that share their modules (`savante.js`, `faicey.js`,
`pythai.js`, `uiftabs.js`):
- The **public edition** (`space/`) is served at PYTHAI/savante.
- The **interactive edition** (`space/interactive/`, layered over the shared files) is served at Gregory-L/Savante. It
  adds Savante in the browser through browseML.

Both editions float the **ultimate input field** over every room, and the field **holds the rooms as tabs**
(`uiftabs.js`). Its button row is a tab strip, with one button per room, the open one marked. T mode takes the same
names as commands (`faicey`, `pythai`, `room <name>`). The public edition's strip ends with the model's on/off switch;
the field asks through the carrier chosen in Ask's model bar, and only while the switch is on. Every other field button
sits under **+**. The header nav stays in the markup as the fallback, and steps aside only once the field has mounted.
**savanteML** (`savanteml.js`) is Savante running in the visitor's browser: browseML, bankML compiled to WebAssembly,
downloads Bonsai-1.7B once (248 MB), verifies every byte against its pin, and puts a receipt on every answer. Both
editions offer it ("this browser" in Ask's model bar), and nothing typed leaves the device.

The **Cluster** room (`cluster.js`) lends that engine to distributed.mind: dmind at mindx.pythai.net, whole jobs, each
answer receipt-checked and audited. What a browser gives is measured in **ITE** (dmind 1.7.0): one token through a
1-billion-parameter model, so one Bonsai-1.7B token is 1.72 ITE. The measure is the same for CPU, RAM and GPU, with
core-, GPU- and RAM GB-seconds kept beside it. A host may pay it per kITE in BANKON PAI through paymint. PAI is a USD basket of USDC, USDT and DAI / USDS, averaged
at 18 decimals, so a rate is a dollar price per million ITE. PAI is not
deployed yet, so nothing is payable today. Contributing happens only on the host's own copy of the room
(`/savante/office/`, `serve.py --host-edition`), so the realm token never leaves the host's origin. The Hugging Face
copies show the pool, measure this browser, and link there.

The build bundles (`uif-space.*` from ultimate-bankml-ui, `browseml*.wasm` and the model's FORK.json from bankML) are
not canon: each Space holds its own copy, and the mirror sync never touches them.

Serve either edition with `python3 space/serve.py [--edition interactive --bundles DIR]` (127.0.0.1:7864; `#faicey` and
`#pythai` open a room directly). The mirror sync publishes each edition from the same layout function. The Gradio
surface `ui.py` carries the same two rooms as tabs.

- **Faicey** is the office embodied, built into one face. The left half is the machine with the skin taken off,
  and the **controls live on it**. The right half is the human: the unplated half of the named artwork
  (`gfx/Savante3.png`, mirrored for display; the bytes are unchanged).
  - The **mouth is an oscilloscope** of the audio actually playing. It reads **voaicey** (`/voicey`, persona
    `savante`, ≤240 characters, the server's own presets) through a Web Audio analyser. Where voicey refuses the
    page's origin, the browser voice speaks instead and the mouth draws a labelled envelope: "not measured".
  - The **eye is the visitor's camera**, in the machine socket opposite the human eye.
  - The **ear is the visitor's microphone**. It drives ring meters, and optionally the mouth.
  - Both senses are opt-in and stay in the browser, and leaving the room stops them. It is a render, not a
    measurement: faceprint and voiceprint stay null and nothing computes them.
- **PYTHAI** reads [huggingface.co/PYTHAI](https://huggingface.co/PYTHAI) with public GETs: every model, dataset and
  Space the org holds, sortable and filterable, with a full Hub reading on any model. It also reports whether each
  mirror above carries canon main (AGREES · BEHIND · DIFFERS · unreadable), with canon main read live from GitHub.
  It has no write path, signed in or not.
- The other rooms are Ask Savante, Settings, About, Hub, The Office, Verdict, Integrity and Skills. Each mirror's
  README describes them.

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

## Carriers and the boardroom seat

The charter pins no model (`sAGI.model`: `pinned: false`), so which model *carries* the office is a claim, and it
is decided like every other claim. The sAGI engine's
[carrier test](https://github.com/cryptoAGI/sagi/blob/main/engine/CARRIER_TEST.md) grades form (the verdict
contract's shape, by regex) and substance (the four invariants, by reading) on five probes with fixed evidence.
On 2026-09-26 it ran through **SavanteUI**, a local Gradio surface that mounts this repository's `ui.py` rooms
behind an Interaction tab, with these results:

| carrier | pass · partial · fail | as a carrier |
|---|---|---|
| Bonsai-8B, 1-bit, on two CPU cores | 5 · 1 · 4 | **REJECT** for review duty: it never used DEFER, and it approved a false claim |
| gpt-oss-120b | 6 · 4 · 0 | **APPROVE_WITH_CONDITIONS**: DEFER only where the operator signs; quote counts from the evidence |

The [transcripts](https://github.com/cryptoAGI/sagi/blob/main/engine/carriers/2026-09-26/TRANSCRIPTS.md) are
published verbatim. A carrier's APPROVE gates nothing until that carrier has passed.

The same day, the office took a seat. `savante_sagi` is the **9th seat, sAGI, of the mindX DAIO boardroom**,
beside the CEO and the seven soldiers (generation 8). Its verdict is cast as a vote: APPROVE and
APPROVE_WITH_CONDITIONS count as approve, REJECT counts as reject, and **DEFER holds the session for the
operator** instead of executing. That last rule is the contract's own "block and page a human", enforced by the
boardroom and not merely requested of the model. In the boardroom's cloud/auto mode the seat runs on the carrier graded APPROVE_WITH_CONDITIONS (gpt-oss-120b); in local mode it runs qwen3:1.7b, which has not been carrier-tested. It
holds no wallet and no mint: the registry lists the seat at tier 0, "unverified", its own word for no identity.


The skill improves itself by measurement (generation 9): **improve.skill**, which started at v0.0.1. Each interaction is written to
`.claude/skills/sagi/.memory` as it happened, with the engine's own token counts; `bind/skill_history.py` derives
`.history` from it, and `SKILL.md` changes only by the improvements `.history` names. An interaction counts only if it
was a single delivery, ended on its own inside a token limit set once, and motivated at most one change with its
evidence. The version is the count, and 1.0.0 is 1000 verified interactions. The first one found that the skill called
two different sentences "doctrine" without saying so; the skill now names both.

**Where the loop stands (2026-11-25): improve.skill v0.0.38.** That is 38 verified interactions and 1 refused, out of
39 lines. Thirty-eight of the lines were answered on the free public CPU lane and published in
[PYTHAI/savante-loop](https://huggingface.co/datasets/PYTHAI/savante-loop); this canon's `.memory` now carries all
of them. The committed record was a byte prefix of the published one, and `bind/skill_history.py` derives a
`.history` byte-identical to the published `.history`. Only the first line motivated a change, and SKILL.md's own
line still reads v0.0.1, because the skill changes only by an improvement `.history` names.

**"Verified" checks the delivery, not the answer.** It means one delivery that ended on its own inside a token limit
set once. Whether the answer was right is a separate question, and the record answers part of it.
- Ternary-Bonsai-8B is the public page's default carrier, and it has not been carrier-tested. It answered **DEFER**
  three times (lines 10, 12, 38) to "our model is production ready because the demo worked", where the charter calls
  for REJECT.
- Bonsai-8B answered **APPROVE_WITH_CONDITIONS** to the same claim (line 11).
- The page now labels each carrier with this evidence.

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
| `bind/savante_bind.py` | The operator's binder — writes the three derived files (the card, the ledger and the THOT manifest `savante.thot.json`). Savante audits it and never runs it. |
| `bind/savante_verify.py` | The holder's checker — recomputes every digest from raw bytes and prints the verdict block; exits 0 only on `VERDICT: APPROVE`. |
| `bind/verdict_record.schema.json` | JSON Schema for a ledger entry; `verdict` is a four-value enum, so a fifth verdict fails mechanically. |
| `gfx/Savante3.png` | The artwork the operator named (the bust). Its sha256 is in the ledger's `image_candidate`; not pinned, so the card's `image` is null. `gfx/README.md` indexes every image of Savante. |
| `PROOF.md` · `PROOF.sha256` | sha256, bytes and predicted CID of this skill and every file that carries a proof, plus the ledger's roots. `sha256sum -c PROOF.sha256` checks them. |

Plain facts, kept on the front page because they are the ones a buyer would
most want elsewhere:

- **Nothing is minted** — not even a dry run. Evidence: no `savante.*` facet
  exists in mindX `agents/blockchain/` (the directory holds `abi_codec.py`,
  `agent_factory.py`, `algorand_verifier.py`, `contracts.py`, `facets.py`,
  `__init__.py`, `template.agent`, `template.model` and a `__pycache__/`;
  `ls`, 2026-09-03), and `/home/hacker/mindX/data/godel/thot/` does not exist
  (`ls`: No such file or directory, 2026-09-03). The ledger records
  `"mint": null`.
- **MIT licensed, and published** (committed in `0853a34`, author and commit date
  2026-09-12T23:58:37-06:00, which is 2026-09-13 05:58 UTC; holder line set in
  `29f03bd`). `LICENSE` at the repository root reads
  `Copyright (c) 2026 cryptoAGI — Professor Codephreak`, and GitHub reports the
  repo's licence as MIT, so `iNFT.md` condition 1 is closed publicly, not only on
  the author's disk. Deciding check, run against the URL rather than the disk:
  `gh api repos/cryptoAGI/savante/license --jq .license.spdx_id` prints `MIT`.
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
