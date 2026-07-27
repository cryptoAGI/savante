# Savante as a Service — how sAGI works with Claude

sAGI is not a model. It is a **charter run on a frontier model** — currently
Claude — under a harness that gives it read-only tools and a fixed verdict
contract. Everything Savante *is* lives in two plain-text files; duplicating
those files duplicates the service. This document explains the mechanics and
the duplication paths.

## 1. The mechanics — what Claude does with these files

**The charter** (`.claude/agents/savante.md`) is a Claude Code *subagent
definition*. Frontmatter declares the name, the delegation trigger
(`description`), and the tool allowlist; the body becomes the agent's system
prompt. Claude Code registers every `.claude/agents/*.md` at session start as
an agent type that the orchestrating Claude can launch:

- `tools: Read, Grep, Glob, Bash` — Savante can read anything and run
  verification commands (tests, builds, `git log`), but has **no Edit/Write**.
  Read-only oversight is enforced by the harness, not by trust.
- The subagent runs in its **own context window** — it reads hundreds of files
  without polluting the caller's context, and returns only the verdict.
- The model is inherited from the session (no pinning — per doctrine, the
  charter must work on whatever frontier or local model carries the session).

**The skill** (`.claude/skills/sagi/SKILL.md`) is the invocation surface.
`/sagi` (or trigger phrases like "have savante review …") loads the skill,
which tells the orchestrator to launch the `savante` agent — and, critically,
defines the **fallback**: if the agent type is not registered (fresh checkout,
mid-session install), launch a general-purpose agent whose prompt begins
*"FIRST: Read `.claude/agents/savante.md` and adopt it as your operating
charter."* The charter file is the single source of truth either way.

**The verdict contract** is the API. Every review returns FINDINGS (file-and-
line evidence + explicit *not yet known* entries with deciding experiments),
then `VERDICT: APPROVE | APPROVE_WITH_CONDITIONS | REJECT | DEFER`, RATIONALE,
numbered verifiable CONDITIONS, and RISKS WATCHED. Because the shape is fixed,
callers can parse it.

## 2. Duplication — Savante in any repository

The service replicates by copying two files:

```bash
git clone https://github.com/cryptoAGI/savante
cp -r savante/.claude/agents/savante.md   <target>/.claude/agents/
cp -r savante/.claude/skills/sagi         <target>/.claude/skills/
```

Per-repo adaptation touches only the **"Canon you measure against"** section
of the charter — point it at the target repo's own doctrine documents. The
epistemology (objective truth, verification-or-unknown), the verdict contract,
and the standing constraints are the invariant core; the canon list is the
plug-in point. A Savante with no canon listed still works: it measures claims
against the code itself.

For all-projects installation on one machine, copy into `~/.claude/agents/`
and `~/.claude/skills/` instead.

## 3. Service modes

**Interactive** — inside Claude Code: `/sagi` or "have savante review
\<target\>". The orchestrator launches the subagent and relays the verdict.

**Headless / CI gate** — Claude Code runs non-interactively with `-p`:

```bash
claude -p "Invoke the sagi skill: review the diff on this branch against main.
Print ONLY the verdict block." --allowedTools "Read,Grep,Glob,Bash"
```

Wire that into a GitHub Action on `pull_request` and grep the output for
`VERDICT: APPROVE` to gate the merge — Savante as a required check. REJECT
fails the job; CONDITIONS become review comments.

**Programmatic (Claude Agent SDK / API)** — for a hosted endpoint (e.g. a
`POST /savante/review` route in a backend), run the charter body as the
system prompt with an agentic tool loop restricted to read-only filesystem
tools, temperature low, and the verdict contract as the required output
format. The charter file is loaded at request time so the service and the
repo never drift apart.

**Scheduled** — a cron'd headless run ("review everything that changed this
week; render one verdict per subsystem") turns Savante into a standing audit
service: *rarely intervenes, always watching* — literally.

## 4. What makes it sAGI and not a linter

A linter checks rules. Savante checks **claims** — it runs the tests and
reports the actual count, reads the git state and reports the actual drift,
greps for the capability a document asserts and reports whether the code
exists. Its distinguishing behaviors, all charter-enforced:

1. **Verification or unknown** — nothing in a verdict is inferred; what could
   not be verified is listed as *not yet known* with the experiment that
   would decide it.
2. **Honest labeling** — it will approve a system that honestly labels its
   own limitations (Tier-C today, Tier-Q target) and reject the same system
   if it overstates them. The claim, not the capability, is what fails.
3. **Refusal to exceed its authority** — DEFER exists because some decisions
   require the operator's signature, and knowing the boundary of your own
   authority is part of knowing.

Duplicated widely, that is the service: every repo, every org, every CI
pipeline gets a chairman that has actually read the code.

---

*Savante knows. Knowledge is what survives verification; nothing else counts.*
