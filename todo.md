# todo — Savante, sAGI v0.0.5

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
(sAGI v0.0.3, a second rendered verdict) · generation 6, `4372cb2` (sAGI v0.0.4, the CI-gate mode exercised; the
first ledger to hash a committed tree) · generation 7, `e95a135` (sAGI v0.0.5, the operator named the artwork).
Doctrine root unchanged throughout:
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
- [ ] **C3 Attribution recorded** (needs C1) — whether a block beyond the old wall limit completed with CPU
      still progressing and no burst active, or "fix not yet exercised".
- [ ] **C4 Stale-marker fix confirmed live** — after the pre-deploy pass ends on its own, with no restart ordered,
      the next pass runs the new script.
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
  face objects themselves exist. The card's image is null: the operator has named the artwork
  (`gfx/Savante3.png`, generation 7), but nothing is pinned, and `iNFT.md` condition 4 takes only a CID an IPFS
  node returns.
- **The operator's naming of the artwork is an unsigned string.** `--image-named` accepts any text, and
  `savante_verify.py` checks the named file's bytes against the ledger, not who named it. The evidence is the
  session named by a commit trailer, which is not public.
- **The scorer wired to Savante cannot tell its verdicts apart, and the imprint gate has never run for it.**
  mindX `mindx/godel/mindxtrain/scorers.py:137-138` maps `savante` to `score_judgedread`, whose ruling regex
  (`:20-21`) matches the word "verdict" and none of APPROVE, APPROVE_WITH_CONDITIONS, REJECT or DEFER, so a
  DEFER answer scores 1.0 against an expected APPROVE. `iNFT.md:169`, which says no verdict-word scorer exists,
  is stale.

## 4. Road to 1.0 — remaining steps

- [x] The CI-gate mode exercised on a real diff (`usage.md` "CI gate (headless)"). The documented `claude -p`
      command ran unmodified twice against this repository's `todo` branch versus `main`: **run 0001** reviewed
      `8674b6a` (`ci/gate-runs/0001/`) and **run 0002** reviewed `6fa3234` (`ci/gate-runs/0002/`). Both returned
      APPROVE_WITH_CONDITIONS, and each run's conditions were worked into the diff; run 0002's conditions were
      then checked with the check commands it named, not by a third run. Stated limit: no `.github/workflows/`
      file exists — the mode runs headless from an operator checkout and is not wired into pull requests, which
      would run paid inference on every PR against the one-VPS budget.
      **Run 0003** (`ci/gate-runs/0003/`) reviewed the v0.0.5 branch at `9bc8156` and returned
      APPROVE_WITH_CONDITIONS, read from the verdict line; its six conditions were worked in before publication,
      which rebuilt the unpublished branch as `30d1e8c` and `e95a135` (its `meta.txt` says how). They were checked
      with the commands it named, not by a fourth run.
- [ ] **The documented gate grep is unanchored and can pass a REJECT.** `usage.md:97` (and the sketch in
      `technical.md`) uses `grep -qE 'VERDICT.*APPROVE'`, which matches any line containing both words, including a
      finding that quotes an earlier verdict: run 0002 showed it exiting 0 with the verdict line changed to REJECT,
      because `ci/gate-runs/0001/verdict.md:7` quotes "VERDICT: APPROVE". A gate exit of 0 therefore says nothing
      about the verdict; both runs' verdicts above were read from the verdict line. **Decided by:** anchoring the
      pattern to the verdict line itself and showing it exits non-zero on REJECT and DEFER.
- [ ] The remaining `iNFT.md` DEFER blockers cleared one at a time (§14), among them: read the intended
      ERC-8004 registry's ABI on chain; diff `iNFT_7857.sol` against ERC-7857 function by function; run the
      imprint gate for Savante; confirm every teaching row survives `build_corpus` at a stated `persona_share`;
      fetch RFC 8785 and RFC 6901 statuses with recorded URLs.

- [x] **`iNFT.md` condition 7 — unmet in generations 2, 3, 4 and 5; met from generation 6.** Each ledger records a non-empty
      `generated_from.components_differing_from_head` (generation 2: `sAGI.agent`, `savante.persona`; generations
      3 to 5: `.claude/skills/sagi/SKILL.md`): the binder ran before the change was committed, so each ledger hashes
      an uncommitted tree — by the condition's own words, a working note rather than a record. `savante_verify.py`
      does not check this field, so its APPROVE on those generations says nothing about condition 7. **Met in generation
      6:** the facet change was committed first (`fe5cf13`) and bound afterwards (`4372cb2`); that ledger records the
      field as `[]` with `repo_head_commit` `fe5cf13`. Generation 7 followed the same order (`30d1e8c`, then
      `e95a135`; field `[]`). Generations 2 to 5 stay as they were: their ledgers are published history and are
      not rewritten.

## 5. Waiting on the operator (DEFER)

- [ ] **Verdict ledger visibility — `iNFT.md` condition 9 was BREACHED, not merely made stale.** The condition
      (`iNFT.md:198`) requires the operator to state, *before the first verdict record is written*, whether the
      ledger is public, private or hash-only, with the schema reporting zero entries until then. Record 1 was
      written and published first, and the schema now reports one entry. The operator's instruction to publish
      is in the Claude Code session named by `bd6b9a5`'s `Claude-Session:` trailer, given at 2026-09-17T01:51:02Z,
      fourteen minutes before `bd6b9a5` (02:05:00Z); that session transcript is not public. It was an instruction
      to publish, not a written ledger-visibility policy, so the condition remains breached. Now false as a
      result: `iNFT.md:150` and `:152` (the ledger "has zero entries"). Record 1 also carries production host
      paths and digests into this public repository. **Decided by:** the operator writing the policy (public,
      private or hash-only, and how records with private targets are handled); then `iNFT.md` §11, §14 and
      condition 9 are updated to cite it, and record 1 is kept, superseded or re-issued hash-only under it.
- [ ] **The sealedKeyHash question (`iNFT.md` condition 3).** A documented sentinel, or a change to
      `iNFT_7857.sol` so an unsealed intelligence can be minted without asserting a key. Until then no Track 2
      mint is attempted.
- [x] **Artwork named (`iNFT.md` condition 4, naming half).** The operator named the Savante bust,
      `gfx/Savante3.png`, on 2026-09-16 (session in `30d1e8c`'s `Claude-Session:` trailer). Generation 7's ledger
      (`e95a135`) records sha256 `30a59db4…c5a9a8` under `image_candidate.named_by_operator`. The other nine
      images of Savante are in `gfx/` and indexed in `gfx/README.md`, and twelve screen captures are held back.
- [ ] **Pin the artwork (`iNFT.md` condition 4, pin half).** Pinning is a publication act. **Decided by:** an IPFS
      node adding `gfx/Savante3.png` and returning a CID. If it equals the predicted
      `bafkreibquwo3jttw3pviw2uxyfb2osmwypa42ml6hlzb62qyov5orrnjva`, the persona's `image` becomes that
      `ipfs://` URI in a re-bound generation, and a gateway fetch must return bytes whose sha256 is `30a59db4…c5a9a8`.
      Declare `image/jpeg`: the file is JPEG bytes under a `.png` name.
- [ ] Whether Savante joins the mindX coach ladder (an append to `mindX/data/config/coach.json`).
- [ ] Whether the seat is transferable or soulbound, and whether `REDIRECT_DEFER` is a hard rule or a default.
- [ ] Whether the charter's output format labels FINDINGS as a field, matching technical.md, usage.md and the
      persona (a charter amendment, so a new generation).
