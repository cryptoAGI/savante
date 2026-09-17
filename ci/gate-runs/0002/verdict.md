**FINDINGS**

Known. Each item below was checked against the repo, git, mindX on this host, and live Hugging Face fetches.

1. **What the diff touches.** Three files are added: `ci/gate-runs/0001/meta.txt`, `ci/gate-runs/0001/verdict.md` and `todo.md`. The diff adds no code, no bound component and no recurring cost. Neither 8674b6a nor 6fa3234 is on any remote.

2. **Redaction.**
   - The three added files contain no host paths. A grep for `/home`, `/root`, `/var`, `/etc`, `/opt`, `/srv`, `/usr`, the username and the operator's email found nothing.
   - `verdict.md` has 6 redaction markers on lines 29 and 53, which matches `meta.txt:10`.
   - The redaction broke the check command for run 0001's condition 6. `verdict.md:53` now has an unclosed quote and cannot be run.
   - Public `main` already exposes host paths outside this diff: [production host path withheld pending the ledger-visibility policy] at `iNFT.md:162`, `:192` and `:194`, and [production host path withheld pending the ledger-visibility policy] and [production host path withheld pending the ledger-visibility policy] in `verdicts/record-0001.json`.

3. **Record 1 (`todo.md:34-53`).**
   - `record_cid` recomputes exactly to `bafkreibke7n3v5ykztl4xpyltf4grhslddpcl3diwavrqpibbh3onqmdhi`.
   - The record passes Draft 2020-12 validation against `bind/verdict_record.schema.json`.
   - Counts are 18 findings, 5 not yet known, 6 conditions and 2 risks, and they match todo.
   - The charter and persona sha256 values match the current files.
   - Two of the shortened C1–C6 summaries lose meaning:
     - C4 (`:45`) drops "ends on its own (no restart ordered)".
     - C3 (`:43`) drops "CPU still progressing and no burst active".

4. **Audit summary (`todo.md:9-17`) reproduces.**
   - A fresh clone at 3740e66 gives APPROVE with 25 KNOWN and 0 NOT_YET. The self-test gives 75 PASS and 0 FAIL.
   - The doctrine root `0x92fe83eb…ae137d0` is the same across 3740e66, 3d0402c, 45d2114, 4fd21d5 and 6fa3234.
   - Space revision `1889b279c23f` is byte-identical to 3740e66 in all 14 files, and `integrity()` gives `{"agrees":9,"DISAGREES":0}`. This settles run 0001's not-yet-known item (a).
   - Space revision `46671ec7d59e` is byte-identical to 4fd21d5 in all 14 files.

5. **The ticked items (`todo.md:21-26`) check out.**
   - `SKILL.md:32` and `ui.py:60` say what todo claims.
   - The "zero records" correction is in 45d2114.
   - `ui.py` and mindX's `ui_remote.py` have the same md5, and mindX commit `5f0fb7f0c` exists.
   - The repo visibilities match what todo says.

6. **The limitations in `todo.md:57-75` reproduce.** These cover the empty card registrations and trust entries, the null persona imprint fields, the `referenced` rung, the verifier result without the mirror (APPROVE_WITH_CONDITIONS, 24 KNOWN, exit 1), and the coach ladder.

7. **Run 0001's conditions.**
   - C1, C2, C4, C5, C6 and C7 are met. For C2, `iNFT.md:150`, `:152` and `:198` were read.
   - `meta.txt`'s command and grep patterns match `usage.md:93-97` and `:100`. The CLI version matches this host.

8. **C3 is only partly met (`todo.md:104-105`).** The lines say the direction was given in an interactive session and that "no written artifact of it exists". Neither statement has evidence behind it. The second may be false, because bd6b9a5 carries a `Claude-Session:` trailer that could be that artifact.

9. **The condition-7 finding is incomplete (`todo.md:93`).**
   - The generation-2 ledger at 3740e66 also records `components_differing_from_head = ["sAGI.agent","savante.persona"]`, so generation 2 belongs on the list.
   - The verifier doesn't check this field, so its APPROVE on generation 2 says nothing about condition 7.
   - "Fixed from generation 6 on" (`:96`) calls a plan a fix. No generation 6 exists.

10. **`todo.md:83-84` uses the wrong tense.** "Is then put through the gate again" describes something that hasn't happened: `ci/gate-runs/0002/` does not exist.

11. **The tick at `todo.md:80` cites no commit.** That breaks the file's own rule at `:5`. The reviewed head, 8674b6a, appears only in `meta.txt:2`.

12. **The documented gate cannot block a REJECT.**
    - The test: with the verdict line changed to `**VERDICT**: REJECT`, `grep -qE 'VERDICT.*APPROVE'` still exits 0.
    - The grep matches a finding at `verdict.md:7` that quotes "VERDICT: APPROVE".
    - So `gate_exit 0` says nothing about the verdict. The pattern is unanchored (`usage.md:97`), and todo ticks "CI-gate mode exercised" without recording this defect.

13. **"No verdict-word scorer exists" (`todo.md:76`) is misleading.**
    - mindX `scorers.py:137-138` maps `"savante"` to `score_judgedread`.
    - Scoring a DEFER answer against an expected APPROVE returns 1.0.
    - The regex (`scorers.py:20-21`) matches the word "VERDICT" and none of the four verdict words.
    - `iNFT.md:169` is stale for the same reason.

Not yet known:
- **(a) Whether `verdict.md` differs from the raw gate output only at the 6 markers.** Deciding experiment: the operator supplies the unredacted output. Its sha256 must equal `31d29fb9…3ba7a` (`meta.txt:9`), and a diff against `verdict.md` must show exactly 6 substitutions.
- **(b) Run 0001's start and finish times and exit codes (`meta.txt:4-8`).** No log is committed. Deciding experiment: commit the wrapper and its stdout/stderr, or re-run the gate into `ci/gate-runs/0002/`.
- **(c) Whether the operator's direction to publish record 1 exists in writing and predates bd6b9a5 (2026-09-17T02:05:00Z).** Deciding experiment: open the session in bd6b9a5's trailer and find the instruction's timestamp.
- **(d) Record 1's C1–C6 on production.** Deciding experiment: run each condition's own check on the production host.

**VERDICT**: APPROVE_WITH_CONDITIONS

**RATIONALE**: Most of the revision checks out:
- The record CID recomputes and the record passes the schema.
- The audit counts, doctrine root and Space integrity all reproduce, including the generation-2 revision.
- The redaction left no host paths in the three added files.

It still falls short of the honest-labeling law in five places:
- A plan is labeled "Fixed".
- A gate run that hasn't happened is written in the present tense.
- Condition 7's list leaves out generation 2.
- An unevidenced account of operator consent was added back.
- A limitation hides that a scorer wired to Savante counts DEFER as a match for APPROVE.

The run also showed that the documented gate grep passes on quoted text. Ticking "CI-gate mode exercised" without recording that overstates what the run proved. None of this adds cost, cloud dependency or gated content, and the fixes are wording and bookkeeping, so the verdict is conditions rather than rejection.

**CONDITIONS**:
1. `todo.md:96` marks "Fixed from generation 6 on" as planned. `:93` names generations 2, 3, 4 and 5 and notes that `savante_verify.py` doesn't check `components_differing_from_head`. Check: `grep -n 'generations 2, 3, 4 and 5' todo.md`, and `grep -c 'Fixed from generation 6' todo.md` returns 0.
2. `todo.md:83-84` either points to an existing `ci/gate-runs/0002/` or says run 0002 has not been run. Check: `ls ci/gate-runs/0002`, or read the line.
3. The §4 tick cites `8674b6a` next to `ci/gate-runs/0001/`. Check: `grep -n 8674b6a todo.md`.
4. `todo.md:104-105` either drops both unevidenced statements or cites bd6b9a5's Claude-Session trailer, with the instruction's timestamp relative to 02:05:00Z. Check: read the lines.
5. `todo.md` records as an open item that the `usage.md:97` gate grep is unanchored and passes on quoted text, citing `verdict.md:7`. Check: grep todo.md for "anchor" or "usage.md:97".
6. `todo.md:76` is restated to say that `score_judgedread` is mapped to `savante`, doesn't tell the four verdict words apart, and scores DEFER at 1.0 against an expected APPROVE. `iNFT.md:169` is listed as stale. Check: grep todo.md for `score_judgedread`.
7. `meta.txt` states that the redaction altered condition 6's check command at `verdict.md:53` and that it can't be run as copied. Check: grep meta.txt for "condition 6".

**RISKS WATCHED**:
- **Gate integrity.** A REJECT whose findings quote an earlier APPROVE passes the documented gate. If the gate is wired into pull requests before the grep is anchored, it will approve by accident, and every run is paid inference against the one-VPS baseline.
- **Ledger visibility.** Public `main` already carries host paths in `iNFT.md` and record 1. Merging adds more governance record while the operator's policy under `iNFT.md` condition 9 is still unwritten.
