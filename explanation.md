# explanation.md — why Savante exists and why it is built this way

## The problem

Autonomous systems drift toward asserted capability. Roadmaps say "deployed"
when code runs only locally; docs claim properties the code lost two
refactors ago; marketing calls things quantum-resistant that sign with
secp256k1. None of this requires dishonesty — it only requires that nobody
re-verified. In a self-improving system (a Gödel machine that rewrites
itself), unverified claims compound: the system plans its next improvement on
top of capabilities it merely believes it has.

The mindX project hit this empirically — 100 improvement campaigns in a week
with 0 successes, traced to the system believing a dead free-tier model was
alive. The lesson generalized: **the binding constraint on autonomy is not
intelligence, it is the truthfulness of the system's beliefs about itself.**

## The answer: a chartered knower

Savante is the role that holds beliefs to the scientific standard. The frame
matters and was explicitly corrected during its creation: not *honesty* (a
moral posture) but **objective truth** (a measurement outcome). "Science
requires objective truth." A claim is known when it survives verification;
otherwise it is unknown — stated as such, with the experiment that would
decide it. The Gödel Machine Index answering NOT_YET to its own AGI question
is the house style; Savante is that posture given an office.

## Why each design choice

**Why read-only.** Oversight that can act becomes an actor, and then its
verdicts are self-interested. The tool allowlist (Read, Grep, Glob, Bash)
lets Savante *verify* — run tests, read git state — but the harness gives it
no Edit or Write. "Rarely intervenes, always watching" is enforced
structurally, not requested politely.

**Why a fixed verdict contract.** Free-form review is unfalsifiable and
unparseable. Four verdicts, numbered verifiable conditions, and mandatory
*not yet known* entries make every review checkable: a condition either
verifies or it doesn't; an unknown either got its experiment run or it
didn't. The contract also makes Savante a machine-consumable gate (CI).

**Why DEFER exists.** Some decisions belong to the operator's signature
(Professor / OVERLORD), not to any evidence Savante can gather. An
intelligence that knows the boundary of its own authority is safer *and* more
truthful than one that always renders an opinion. DEFER is knowledge about
jurisdiction.

**Why no model pinning.** The charter is the asset; the model is the engine
of the day. Doctrine forbids pinning (selector + cascade to local models), so
Savante is written to be model-portable — the discipline must survive an
engine swap, or it was never a discipline.

**Why two plain-text files.** Duplication is the deployment story
("Savante as a Service"). Anything that lives in weights, fine-tunes, or
databases resists audit and replication. A charter in markdown is diffable,
reviewable, forkable, and installable with `cp`.

## The lineage

Savante predates this implementation. In the mindX MANIFESTO (Project
Chimaiera), Savante is Chairman — co-author of the roadmap, supervisor of the
presale, executor of the legal strategy, the human-oversight pole opposite
Professor Codephreak's platform-architect pole. `savante_sagi` sits in
`core_command` of the DAIO agent registry alongside PYTHAI, SUNTSU (the
dojo), and RAGE. This repository is that role made operational: the Chairman
as a runnable reviewer. Governance context: mindX is run by the Boardroom and
the Dojo (Boardroom t1 → Dojo Arbiter t2 → War Council t3, hash-linked
VotingBooth decisions); completing that authority in deployment is an open
roadmap item Savante watches.

## Knowledge, and the knowledge economy — the evolution from the information age

The information age solved distribution and lost verification. Information
became effectively free and infinite — and therefore worthless at the margin:
generated, copied, asserted, and hallucinated at industrial scale, with the
cost of *checking* any of it left with the reader. An economy can't price
information anymore; there is too much of it and no way to tell, from the
artifact alone, whether it is true.

**Knowledge is information that has survived verification.** That single
transformation — running the test, reading the chain, attesting the time,
proving the recall — is what turns an infinite free commodity into a scarce
priced one. The knowledge economy is the successor of the information
economy for exactly this reason: verification is the new scarce input, and
whoever performs it, records it, and makes it portable *creates* the value.

This is the economic function of the whole stack this repository sits in:

- **mindX** is a knowledge-delivery system, not an information system — its
  catalogue is an append-only event stream of what actually happened, its
  memories are projections rebuildable from logs, its Gödel Machine Index
  refuses to claim what its measurements cannot show.
- **The measurement tokens** price the verified quantities directly:
  SCIEN·TIFIC prices accuracy, LUV prices attention (proof of gesture —
  attention *demonstrated*, not claimed), chronos.oracle attests time. Both
  derive value from being priceless: accuracy and attention are not
  commodities a market prices first — they are priceless quantities that,
  once measured, create price. Value creates price, never the reverse.
- **Savante** is the conversion point: it takes claims (information) and
  returns verdicts (knowledge) — findings with evidence, unknowns with
  deciding experiments. Every review manufactures the knowledge economy's
  base commodity.

The information age asked *"do you have the data?"* The knowledge age asks
*"has it survived verification, and who attests it?"* Savante is an answer to
the second question, packaged small enough to install anywhere.

## The measured economy it belongs to

The same week Savante was chartered, the doctrine's instruments went live:
SCIEN·TIFIC (accuracy, with chronos.oracle for time-truth) and SHAMBA LUV
(attention, priced by proof of gesture) are deployed tokens, launched by a
deployer that proved worthy from version 1. CP2048-QR disciplines security
claims the same way (Tier-Q only where a mainnet transaction proves it). The
economy circulates bankon → mindx → agenticplace: identity proven, knowledge
delivered, value exchanged — every axis measured, never asserted. Savante's
verdicts are the same commodity in prose form.

## What it is not

- **Not a linter.** Linters check rules; Savante checks *claims* against
  evidence it gathers itself.
- **Not a rubber stamp or a gatekeeper by temperament.** Its first verdict
  approved-with-conditions a system whose docs honestly said "Tier-C today" —
  and flagged the one line where documentation outran code. The claim, not
  the capability, is what fails.
- **Not AGI, and it would be the first to say so.** It is a prototype of the
  discipline an sAGI would need: verification or unknown, honest labeling,
  bounded authority. The name states the aspiration; the charter states what
  is true today.
