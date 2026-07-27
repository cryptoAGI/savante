# usage.md — operating Savante

Practical instructions: install, invoke, adapt, wire into CI, and read the
verdicts.

## Install

Into one repository:

```bash
git clone https://github.com/cryptoAGI/savante
cp    savante/.claude/agents/savante.md  <your-repo>/.claude/agents/
cp -r savante/.claude/skills/sagi        <your-repo>/.claude/skills/
```

For every project on the machine, use `~/.claude/agents/` and
`~/.claude/skills/` instead.

The agent type registers at the **next** Claude Code session start. Until
then the `/sagi` skill's fallback path works immediately (it instructs a
general-purpose agent to adopt the charter).

## Invoke

Inside Claude Code, any of:

```
/sagi review the payment router changes
have savante review the parsec-wallet production readiness
savante: is this suite deploy-ready?
render a verdict on <claim>
```

Give it a *claim to verify*, not a vibe to discuss: "production-ready?",
"does the code do what QUANTUM.md says?", "should this merge?". Savante
verifies — it runs the tests and reports actual counts, reads the actual git
state, greps for the capability a document asserts. Reviews of a full repo
take minutes, not seconds; that is the verification running.

## Read the verdict

```
FINDINGS       what is KNOWN, with file:line evidence
               + "not yet known" items, each with its deciding experiment
VERDICT:       APPROVE | APPROVE_WITH_CONDITIONS | REJECT | DEFER
RATIONALE:     the deciding constraint, board-minute style
CONDITIONS:    numbered; each independently verifiable
RISKS WATCHED: what Savante keeps watching if this proceeds
```

Interpretation:

- **APPROVE** — the claim survived verification as stated.
- **APPROVE_WITH_CONDITIONS** — sound core, enumerated gaps; the conditions
  are the work list, each one checkable when done.
- **REJECT** — the claim failed against evidence; the rationale names where.
- **DEFER** — the decision belongs to the operator's signature, not to
  gatherable evidence. Treat as "stop and ask the human," never as failure.
- **not yet known** — not hedging: a fact about the current evidence, with
  the experiment that would decide it. Run the experiment, re-review.

Re-reviews: after satisfying conditions, invoke again with "re-verify the
conditions from the last savante review of <target>."

## Adapt to your repository

Edit one section of `.claude/agents/savante.md` — **"Canon you measure
against"** — to point at your own doctrine documents (architecture docs,
ADRs, strategy files). Optionally adjust the standing constraints to your
project's equivalents (budget baseline, governance gates). If your charter
lives at a nonstandard path, update the absolute path in the skill's
fallback instruction. Everything else — epistemology, verdict contract,
read-only tools — is the invariant core; leave it.

No canon at all still works: Savante measures claims against the code itself.

## CI gate (headless)

```yaml
# .github/workflows/savante.yml
name: savante
on: [pull_request]
jobs:
  verdict:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Savante review gate
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          out=$(claude -p "Invoke the sagi skill: review this branch's diff
            against the base branch. Print ONLY the verdict block." \
            --allowedTools "Read,Grep,Glob,Bash")
          echo "$out"
          echo "$out" | grep -qE 'VERDICT.*APPROVE'   # blocks on REJECT/DEFER
```

Use `grep -qE 'VERDICT.*: *APPROVE$'` to also block on
APPROVE_WITH_CONDITIONS. Add a step posting CONDITIONS as a PR comment if
you want the work list surfaced.

## Scheduled audit

```bash
# weekly: one verdict over the week's changes
claude -p "Invoke the sagi skill: review everything changed in the last 7
days (git log --since='7 days ago'); render one verdict per subsystem." \
  --allowedTools "Read,Grep,Glob,Bash"
```

Cron it and route the output wherever your team reads reports. This is the
standing-audit mode: rarely intervenes, always watching.

## Boundaries (by design)

- Savante **never edits files** — it has no Write/Edit tools. If a review
  should lead to fixes, that is a separate, ordinary coding task afterward.
- Savante **does not approve what it has not read**. Point it at what
  matters; it reads before it rules.
- Savante **renders DEFER** rather than guessing on operator-jurisdiction
  decisions. That is the charter working, not a limitation.
