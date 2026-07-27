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
target repo's doctrine documents (and, in the skill's fallback line, the
charter's absolute path if your layout differs). The epistemology, verdict
contract, and standing constraints are the invariant core. With no canon
listed, Savante still functions — it measures claims against the code itself.
