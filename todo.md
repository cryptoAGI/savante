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
      canon's `ui.py` — re-synced in mindX (not a canon change).
- [ ] The public page shows `head` as the commit the binder saw, which is the parent of the commit that
      publishes the ledger (a ledger cannot contain its own commit hash). By design, but a visitor can read
      it as the previous generation. **Decided by:** a label on the page naming it the bind-time HEAD, or a
      sentence in `usage.md`.

## 2. Verdict ledger, record 1 — open conditions

`verdicts/record-0001.json`, APPROVE_WITH_CONDITIONS on the rage render-queue fix (mindX `dad6d6f6d`,
private). The target belongs to mindX; the conditions are tracked here because the office watches them.

- [ ] **C1 Per-call telemetry.** Each piper call appends doc, voice, block, words, wall_s, cpu_s, kill reason.
      **Verified when** the next render of any article adds one row per block.
- [ ] **C2 Honest kill labels.** A kill writes `exc.reason` into the queue log. **Verified by** grepping
      `/var/log/rage-render-queue.log` after a kill for "hung", "CPU budget" or "wall ceiling", or a unit test.
- [ ] **C3 Attribution recorded** (needs C1). An entry states whether a block exceeding the old wall limit
      completed with CPU progressing and no burst, or says "fix not yet exercised".
- [ ] **C4 Stale-marker fix confirmed live.** After the pass that began 2026-09-16 09:42:42Z ends on its own,
      the next pass's fd 10 is a non-deleted `/root/render_rage_queue.sh`, md5 `96217fc7f6d895981916354417b624b2`.
- [ ] **C5 Deploy drift reconciled or labelled** (prod `engines.py` = `32718c009` + `dad6d6f6d`'s hunks).
- [ ] **C6 Manual record edits logged**, and `/root/apply_processor_shares.sh` reconciled with the repo copy.

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
- **Voice, face and image are null**, each with its reason and deciding experiment.
- **No verdict-word scorer exists, and the imprint gate has never run for Savante** (`iNFT.md` §14).

## 4. Road to 1.0 — remaining steps

- [ ] The CI-gate mode exercised on a real diff (`usage.md` "CI gate (headless)").
- [ ] The remaining `iNFT.md` DEFER blockers cleared one at a time (§14), among them: read the intended
      ERC-8004 registry's ABI on chain; diff `iNFT_7857.sol` against ERC-7857 function by function; run the
      imprint gate for Savante; confirm every teaching row survives `build_corpus` at a stated `persona_share`;
      fetch RFC 8785 and RFC 6901 statuses with recorded URLs.

## 5. Waiting on the operator (DEFER)

- [ ] **Verdict ledger visibility (iNFT.md §14, condition 9).** §14 calls it the operator's call "before the
      first record is written". Record 1 has since been published in this public repository at the operator's
      direction (2026-09-17), but the decision itself — public, private, or hash-only, and how records with
      private targets are handled — is not written down, and the §14 sentence is now stale. **Decided by:** the
      operator stating the policy; then §14 is updated to cite it.
- [ ] Whether Savante joins the mindX coach ladder (an append to `mindX/data/config/coach.json`).
- [ ] Whether the seat is transferable or soulbound, and whether `REDIRECT_DEFER` is a hard rule or a default.
- [ ] Whether the charter's output format labels FINDINGS as a field, matching technical.md, usage.md and the
      persona (a charter amendment, so a new generation).
