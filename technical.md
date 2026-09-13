# technical.md — how Savante runs

The complete mechanics: file formats, harness behavior, the verdict contract
as a parseable API, and the wiring for each service mode.

## 1. Repository layout

```
.claude/agents/savante.md      the charter — canonical, installable
.claude/skills/sagi/SKILL.md   the /sagi skill — canonical, installable
savante.md                     top-level mirror of the charter (readable copy)
sAGI.md                        the sAGI definition + full skill text
README.md · explanation.md · technical.md · usage.md · SAVANTE_AS_A_SERVICE.md
```

The two `.claude/` files are the **only functional artifacts**. Everything
else is documentation. If the top-level mirrors and the `.claude/` files ever
disagree, the `.claude/` files win — they are what the harness executes.

## 2. The agent file format

`.claude/agents/savante.md` is a Claude Code subagent definition: YAML
frontmatter + markdown body.

```yaml
---
name: savante          # the agent type name used by the Agent tool
description: >         # WHEN to delegate — the orchestrator reads this
  SAVANTE (SAGI) — chairman-tier strategic oversight ...
tools: Read, Grep, Glob, Bash   # tool allowlist — the authority boundary
---
# body = the agent's entire system prompt
```

Harness behavior that matters:

- **Registration**: Claude Code scans `.claude/agents/*.md` (project) and
  `~/.claude/agents/*.md` (user) at session start. A file created mid-session
  registers for the *next* session — hence the skill's fallback path.
- **Tool allowlist**: `Read, Grep, Glob, Bash` gives Savante full read access
  plus the ability to *run verification* (tests, builds, `git log`, greps).
  No Edit, no Write, no Agent — read-only oversight is enforced by the
  harness, not by the prompt. Bash can still mutate in principle; the charter
  forbids it and the allowlist removes every purpose-built write tool.
- **Context isolation**: the subagent gets its own context window. It can
  read an entire repository and return only the verdict; the caller's context
  receives nothing else.
- **Model inheritance**: no `model:` key — Savante runs on whatever model the
  session runs on (frontier or local). This is deliberate: the doctrine
  forbids model pinning; the charter must be model-portable.

## 3. The skill file format

`.claude/skills/sagi/SKILL.md`: YAML frontmatter (`name`, `description` — the
description doubles as the trigger index) + markdown body of instructions the
orchestrator follows when the skill is invoked via `/sagi` or a trigger
phrase. The body encodes the launch procedure, the fallback (charter-adoption
by a general-purpose agent when `savante` is unregistered), the verification
mandate ("run the tests... actual results only"), and the relay obligation
(subagent reports are invisible to the user; the orchestrator must restate
the verdict).

## 4. The verdict contract (parseable API)

Every review returns, in order:

```
FINDINGS        evidence per load-bearing claim (file:line), plus
                "not yet known" entries each naming the deciding experiment
VERDICT:        APPROVE | APPROVE_WITH_CONDITIONS | REJECT | DEFER
RATIONALE:      2–5 sentences, board-minute style
CONDITIONS:     numbered; each independently verifiable
RISKS WATCHED:  one or two named risks
```

Machine consumption: the verdict line is grep-stable —

```bash
result=$(claude -p "..." )
echo "$result" | grep -qE '^\*{0,2}VERDICT\*{0,2}: *APPROVE' || exit 1
```

`DEFER` is reserved for decisions requiring the operator (Professor /
OVERLORD) signature — treat it as "block and page a human," not as failure.

## 5. Service-mode wiring

**Interactive** — `/sagi <target>` or "have savante review <target>" inside a
Claude Code session. Nothing to wire.

**Headless / CI gate** — GitHub Actions sketch:

```yaml
- name: Savante review gate
  run: |
    out=$(claude -p "Invoke the sagi skill: review the diff of this branch
      against main. Print ONLY the verdict block." \
      --allowedTools "Read,Grep,Glob,Bash")
    echo "$out"
    echo "$out" | grep -qE 'VERDICT.*: *APPROVE' # WITH_CONDITIONS also matches APPROVE_
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

Tighten the grep to `APPROVE$` if conditions must block. Post CONDITIONS as
PR comments in a follow-up step if desired.

**Agent SDK / API endpoint** — load the charter body (strip frontmatter) as
the system prompt; run an agentic tool loop restricted to read-only
filesystem tools over the target checkout; require the verdict contract as
output. Load the charter from disk at request time so service and repo never
drift. A natural mindX home: `POST /savante/review {target, question}` on the
backend, emitting a `savante.verdict` catalogue event.

**Scheduled** — cron a headless run over the week's diff; one verdict per
subsystem. The standing-audit mode: rarely intervenes, always watching.

## 6. Duplication procedure

```bash
git clone https://github.com/cryptoAGI/savante
cp    savante/.claude/agents/savante.md  <target>/.claude/agents/
cp -r savante/.claude/skills/sagi        <target>/.claude/skills/
```

Adapt only the charter's **"Canon you measure against"** section to the
target repo's doctrine documents (the skill's fallback line reads the
repo-relative `.claude/agents/savante.md`; change it only if you install the
charter elsewhere — never to an absolute path, see §7 step 1). The
epistemology, verdict contract, and standing constraints are the invariant
core. With no canon listed, Savante still functions — it measures claims
against the code itself.

## 7. The persona, the ledger, and the binder

Eight more files sit beside the two `.claude/` artifacts as of 2026-09-03.
None of them changes §1: the two `.claude/` files remain the only functional
artifacts of the service, and if a top-level mirror ever disagrees with them
the `.claude/` copy wins (§1, lines 16–18 above).

```
savante.persona             SOURCE OF TRUTH — the mindX persona; carries the
                            `token` block (:186) and the `task` block (:565);
                            shape expanded from the draiml.persona founder template (:7)
savante.agentcard.json      DERIVED — the EIP-721 / ERC-8004 card
savante.commitments.json    DERIVED — the digest ledger (sha256, CIDv1, doctrine root)
bind/savante_bind.py        the OPERATOR's binder: writes the two derived files
bind/savante_verify.py      the holder's checker: recomputes and compares
bind/verdict_record.schema.json
                            JSON Schema for a ledger entry; `verdict` is a
                            four-value enum
sAGI.agent · sAGI.model     the two authored mindX blockchain-agent facets
                            (savante === sAGI.agent; the persona is the third)
```

**Deviations from the implementing spec, recorded.** Two persona sub-keys
are not in the spec's file plan: `token.standards_note` (`savante.persona:190`)
and `task.battery_note` (`savante.persona:610`). Both are loader-inert —
`corpus.persona_task` copies only `name`, `one_thing`, `battery` and
`confirmed_when` (`mindX/mindx/godel/mindxtrain/corpus.py:376-386`). And
`task.confirmed_when.imprint_delta_gt` is the integer `0` where the spec wrote
`0.0`: preflight P2 is whole-document and would fail closed on a float, and
`hf_client.py:2127` coerces the value with `float()` before comparing.

**Precedence.** `savante.persona` is authored; `savante.agentcard.json` and
`savante.commitments.json` are derived from it by `bind/savante_bind.py`,
regenerable at any time, and never hand-edited — each opens with a `$comment`
saying so. A hand edit to a derived file is a defect, not a customization:
the next binder run overwrites it. Derived values never flow back: the
persona's `token.bindings` slots are permanently null by rule, because
writing an `agentId` into the persona would change its bytes and invalidate
the digest a registry would hold (`savante.commitments.json`,
`bindings_rule`).

**Boundary.** The binder is the operator's tool. Savante audits
`bind/` — reads it, runs the verifier, grades the ledger — and never runs the
binder, because oversight that acts is oversight no longer, and that includes
minting (`savante.persona:562`). A mint is a visibility-or-publication
decision and a treasury action, two of the defer triggers at
`savante.persona:136`; the office's own verdict on it is `DEFER`
(`savante.persona:560`). The binder does no network I/O and writes nothing
on chain (`savante.commitments.json`, `mint_reason`).

**Not part of the product.** `bind/` is not part of the duplication in §6.
`cp` of the charter and the skill still conveys the whole office; a copier
receives the office and not the ledger, and should know which is which. The
ledger answers a different question — *is this the persona the author
committed to?* — and needs `savante.persona` plus, for keccak256 only,
`pycryptodome` or `eth_utils` (`bind/savante_bind.py:16`); sha256 and the
CID use the standard library. The verifier needs no network for steps 1–5
and never trusts the author: it recomputes every digest from raw bytes.

**Order of operations.** The sequence that produced the current files is
load-bearing, and it is the order any regeneration must keep:

1. Fix `.claude/skills/sagi/SKILL.md` first. Its fallback path (line 33)
   carried a machine-specific absolute path, `/home/hacker/mindX/...`
   (visible in `git diff` against `HEAD`); it now reads the repo-relative
   `.claude/agents/savante.md`. A digest computed before that fix would have
   frozen one machine's home directory into the authenticity commitment of a
   duplication-first product, permanently.
2. Edit `savante.persona`.
3. Mirror it byte-for-byte to
   `/home/hacker/mindX/mindx/godel/mindxtrain/personas/savante.persona`.
   They are separate inodes and only the mindX copy is on the corpus
   loader's path; an edit landing in one place splits the identity and
   splits the document the ledger commits to.
4. Validate: `python3 personas/persona_project.py --all --check` in
   `mindx/godel/mindxtrain/` must exit 0.
5. Mirror any charter edit to `savante.md` (§1 precedence).
6. Derive the derived facets. `sAGI.prompt` is the charter body verbatim and
   `sAGI.tool` is the allowlist plus the grant mask; the binder regenerates
   both and **fails closed** on drift, printing the offending byte offset and
   the regeneration command. A charter edit that skips this step is caught
   here rather than shipping two disagreeing copies of the system prompt.
7. Validate the embodiment facets. `sAGI.voaice` and `sAGI.faice` must satisfy
   the honest-null rule: `measured` and the print are null together or present
   together, and an unmeasured facet carries both a reason and its deciding
   experiment. A plausible-looking value here would fill a doctrine-protected
   embodiment null (pointer 14) with something nobody earned.
8. Then, and only then, run `python3 bind/savante_bind.py`. It fails closed
   on a mirror md5 mismatch (`bind/savante_bind.py`, the mirror check) and on
   the preflight — every property name ASCII, every number an integer — that
   makes its canonical bytes equal RFC 8785 output (`:19-22`). It writes the
   card, the ledger, and `savante.thot.json`.
9. Nothing else. A mint is deferred.

Regeneration is idempotent: two consecutive binder runs over an unchanged
tree produce byte-identical card, ledger **and manifest** (checked with `cmp`;
first on 2026-09-03 for the card and ledger, and again on 2026-09-11 once the
manifest joined them).
