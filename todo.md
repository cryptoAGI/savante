# todo — Savante, sAGI v0.0.3

Written 2026-09-17 from the audits, releases and verdict of 2026-09-16/17. Every open item names how it is
decided: a deciding experiment someone other than the officer can run, or the operator decision it waits on.
Nothing here is a claim of progress; ticked items cite the commit that closed them.

## 1. Audit summary

Final audit of generation 2 (fresh clone of `3740e66`, 2026-09-16): `bind/savante_verify.py` returned
`VERDICT: APPROVE` with 25 of 25 checks known; `--self-test` passed 75 of 75; every canon file mapped onto the
Hugging Face Space was byte-identical; the page's own `integrity()` in `savante.js`, run in Node against the
bytes the Space serves, reported 9 of 9 ledgered components agreeing.

Releases since: generation 3, `3d0402c` (sAGI v0.0.2, the surface launched and parsed) · generation 4,
`45d2114` (SKILL.md stopped saying the verdict ledger holds zero records) · generation 5, `4fd21d5`
(sAGI v0.0.3, a second rendered verdict). Doctrine root unchanged throughout:
`0x92fe83eb0fb8fb6b9cbde75ee4bbb671032a849ee25d65592b86913d0ae137d0`.

Findings from that audit:

- [x] `ui.py` shows `VERSION = "0.2.0"`, which read as contradicting the sAGI version — SKILL.md now names it
      as the Gradio surface's version, not the office's (`3d0402c`).
- [x] SKILL.md said the verdict ledger holds zero records after record 1 existed — corrected (`45d2114`).
- [x] mindX's staging copy `mindx/savante/ui_remote.py`, described as matching `main`, had fallen behind
      canon's `ui.py` — re-synced in mindX commit `5f0fb7f0c` (a private repository); canon `ui.py` and that
      copy now share md5 `b8d201c5`. Not a canon change.
- [ ] The public page shows `head` as the commit the binder saw, which is the parent of the commit that
      publishes the ledger (a ledger cannot contain its own commit hash). By design, but a visitor can read
      it as the previous generation. **Decided by:** a label on the page naming it the bind-time HEAD, or a
      sentence in `usage.md`.

## 2. Verdict ledger, record 1 — open conditions

`verdicts/record-0001.json`, APPROVE_WITH_CONDITIONS on the rage render-queue fix (mindX `dad6d6f6d`,
private). The target belongs to mindX; the conditions are tracked here because the office watches them.

Record CID `bafkreibke7n3v5ykztl4xpyltf4grhslddpcl3diwavrqpibbh3onqmdhi`. Each condition's exact check —
including the production host paths and digests it names — is in the record's `conditions` array and is not
re-copied here while the ledger-visibility policy (§5) is unwritten.

- [ ] **C1 Per-call telemetry** — one timing and kill-reason row per piper call.
- [ ] **C2 Honest kill labels** — the kill reason reaches the queue log.
- [ ] **C3 Attribution recorded** (needs C1) — whether a block beyond the old wall limit completed, or
      "fix not yet exercised".
- [ ] **C4 Stale-marker fix confirmed live** — the first queue pass started after the deploy runs the new script.
- [ ] **C5 Deploy drift reconciled or labelled.**
- [ ] **C6 Manual record edits logged**, and the deployed shares script reconciled with the repository copy.

Not yet known in that record, each with its deciding experiment (see the record for the full text):
who can credit rage-1509's jaimla success (fix, burst, or neither); whether the 30 % speak-slice cap was the
root cause; the burst's actual `cpu.max` values; when the `.timedout` rename was made; when post 1509 was
published. Risks watched: a starved slice now holds the queue for hours without failing; render failure
history can be erased by hand.

## 3. Limitations, stated rather than hidden

- **Nothing is minted.** `iNFT.md` renders VERDICT: DEFER on binding the office to a token; the agent card's
  `registrations` and `supportedTrust` are empty.
- **No countersignature.** No signing executor exists, so a forged verdict record is detectable only by the
  digests it fails to match, not by a signature it cannot forge.
- **The first verdict has no artifact.** 2026-07-26, parsec-wallet, is prose only; record 1 is the second
  verdict rendered.
- **Record 1 is private evidence.** Its target repository is private: a stranger can check the two public
  audio manifests it cites, not the commit or the file md5s.
- **A stranger's verification is conditional.** Without the author's mindX mirror, `savante_verify.py`
  returns APPROVE_WITH_CONDITIONS (24 known, exit 1), with the mirror md5 as the condition.
- **The doctrine root detects an edit and prevents none.** An owner can edit, re-bind and publish a fresh,
  internally consistent root. Only comparison against the first root written on chain would catch it, and
  nothing is on chain.
- **The rung is `referenced`.** No upload receipt exists, so no higher rung is claimed.
- **What a token would convey is not known.** MIT governs the copy of the files, not token rights.
- **The embodiment prints are null.** `embodiment.voice.voiceprint`, `embodiment.face.faceprint` and
  `embodiment.face.cloneProportions` are null, each with its reason and deciding experiment; the voice and
  face objects themselves exist. The card's image is null and waits on the operator naming the artwork
  (`iNFT.md` condition 4), not on an experiment.
- **No verdict-word scorer exists, and the imprint gate has never run for Savante** (`iNFT.md` §14).

## 4. Road to 1.0 — remaining steps

- [x] The CI-gate mode exercised on a real diff (`usage.md` "CI gate (headless)"). Run 0001, 2026-09-17: the
      documented `claude -p` command, unmodified, reviewed this branch's diff (`todo.md`) against `main` and
      returned APPROVE_WITH_CONDITIONS — `usage.md`'s grep passed (exit 0), the strict `APPROVE$` grep did not
      (exit 1). Its output and metadata are in `ci/gate-runs/0001/`. Every condition it set is addressed in this
      revision, which is then put through the gate again. Stated limit: no `.github/workflows/` file exists —
      the mode was exercised headless from an operator checkout, not wired into pull requests. Wiring it in
      would run paid inference on every PR, and that recurring cost has not been justified against the
      one-VPS budget.
- [ ] The remaining `iNFT.md` DEFER blockers cleared one at a time (§14), among them: read the intended
      ERC-8004 registry's ABI on chain; diff `iNFT_7857.sol` against ERC-7857 function by function; run the
      imprint gate for Savante; confirm every teaching row survives `build_corpus` at a stated `persona_share`;
      fetch RFC 8785 and RFC 6901 statuses with recorded URLs.

- [ ] **`iNFT.md` condition 7 — unmet in generations 3, 4 and 5.** Each ledger records
      `generated_from.components_differing_from_head = ['.claude/skills/sagi/SKILL.md']`: the binder ran before
      the SKILL.md change was committed, so each ledger hashes an uncommitted tree — by the condition's own
      words, a working note rather than a record. **Fixed from generation 6 on** by committing the facet change
      first and binding afterwards. **Verified by:** that field being empty in the generation-6 ledger.

## 5. Waiting on the operator (DEFER)

- [ ] **Verdict ledger visibility — `iNFT.md` condition 9 was BREACHED, not merely made stale.** The condition
      (`iNFT.md:198`) requires the operator to state, *before the first verdict record is written*, whether the
      ledger is public, private or hash-only, with the schema reporting zero entries until then. Record 1 was
      written and published first, and the schema now reports one entry. Operator direction not recorded: it
      was given in an interactive session on 2026-09-17, and no written artifact of it exists. Now false as a
      result: `iNFT.md:150` and `:152` (the ledger "has zero entries"). Record 1 also carries production host
      paths and digests into this public repository. **Decided by:** the operator writing the policy (public,
      private or hash-only, and how records with private targets are handled); then `iNFT.md` §11, §14 and
      condition 9 are updated to cite it, and record 1 is kept, superseded or re-issued hash-only under it.
- [ ] **The sealedKeyHash question (`iNFT.md` condition 3).** A documented sentinel, or a change to
      `iNFT_7857.sol` so an unsealed intelligence can be minted without asserting a key. Until then no Track 2
      mint is attempted.
- [ ] **Artwork (`iNFT.md` condition 4).** The operator names the artwork file or states there is none.
- [ ] Whether Savante joins the mindX coach ladder (an append to `mindX/data/config/coach.json`).
- [ ] Whether the seat is transferable or soulbound, and whether `REDIRECT_DEFER` is a hard rule or a default.
- [ ] Whether the charter's output format labels FINDINGS as a field, matching technical.md, usage.md and the
      persona (a charter amendment, so a new generation).
