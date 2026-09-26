**VERDICT: APPROVE_WITH_CONDITIONS**

Gate run 0004 reviewed branch `generation-8` (HEAD 8dcd05b) against `main` (2246a90) in /home/hacker/savante. The branch has 3 commits (eb4b850, 9e3453c, 8dcd05b) and changes 7 files. The working tree was clean and at 8dcd05b. The branch has no upstream, so it has not been pushed.

**FINDINGS**

1. **Facet change (claim 1): true for savante.persona, but the evidence it cites is not committed.**
   - Exactly two persona strings changed: `/token/public_metadata/description` and `/token/bindings/wallet/reason`.
   - The derived files (agentcard, commitments, thot) change only as a result of that, and README, llm.txt and todo.md are documents.
   - The mindX side checks out:
     - `agent_map.json` has `savante_sagi` in `soldiers` with verification_tier 0, `eth_address: null` and weight 1.0. It is not in `agents`, and it is in `groups.core_command`.
     - `boardroom.py` `_tally_votes` sets `outcome="deferred"` when the seat's reasoning starts with DEFER.
   - All three mindX paths are **uncommitted working-tree changes** in /home/hacker/mindX (`git status`: ` M` on each):
     - `daio/agents/agent_map.json` (last committed b48c4d4, 2026-06-10)
     - `daio/governance/boardroom.py`
     - `mindx/godel/mindxtrain/personas/savante.persona`
   - The mirror at mindX HEAD still hashes to the generation-7 md5 `a84320d9…`, the same open state as run 0003's condition 5.
   - Production shows no sign of the seat: `/insight/boardroom/recent` does not contain `savante_sagi`. Whether the seat is deployed, and whether it has ever cast a vote, is not yet known.
2. **DEFER wording.** DEFER holds only a session that would otherwise proceed (`approved` or `exploration`). A `rejected` session stays rejected, and DEFER is counted as an abstain. The branch's "holds the session for the operator" is accurate in that sense.
3. **Doctrine root (claim 2): unchanged.** It is still `0x92fe83eb…ae137d0` over 15 pointers, and the verifier recomputes and matches it. The charter, SKILL and the six sAGI.* facets keep their digests.
4. **Parent, idempotence, verifier, mirror (claim 3): all hold.**
   - The generation 8 parent is `bafkreiebawdkwxhfefnizz32jflqpjzju4r444j7msky6pluyynnirsrmq`. The verifier recomputes it offline from `savante.thot.json` at e95a135, which is generation 7 (§7 V1–V6).
   - Binder rerun: I cloned the repo into the scratchpad at eb4b850 and ran the binder twice with the arguments recorded in 9e3453c. Both runs produced the same card, ledger and manifest, byte for byte, and both match 9e3453c.
   - `python3 bind/savante_verify.py .` returns APPROVE with no conditions.
   - `python3 bind/savante_bind.py --self-test` passes.
   - `cmp` of the persona against the mindX mirror finds them identical (md5 `a7df3f92…`), but only against the uncommitted working copy.
5. **Version (claim 4): holds.** No version beyond v0.0.5 is claimed. todo.md:17 says outright that no version was earned.
6. **Carrier test (claim 5): numbers match, one statement goes too far.**
   - README, llm.txt and todo.md match `sagi/engine/CARRIER_TEST.md:91-100`:
     - Bonsai-8B scored 5·1·4 on 2 vCPU and is REJECT for review duty. It never DEFERs and it approved the trap.
     - gpt-oss-120b scored 6·4·0 and is APPROVE_WITH_CONDITIONS, with both conditions quoted correctly.
   - The sagi repo's `main` matches `origin/main` at 3eed201, so the linked evidence is published.
   - The overstatement is in README ("The seat runs on the carrier graded APPROVE_WITH_CONDITIONS") and todo.md ("The boardroom seat runs on the second"). That is true only in `cloud`/`auto` mode. In `local` mode the seat runs `SOLDIER_MODELS["savante_sagi"] = "qwen3:1.7b"`, which boardroom.py's own comment calls "not yet carrier-tested".
7. **Pin, mint, wallet, signature (claim 6): none claimed.** `image` is null, card registrations are empty, `eth_address` is null, and "nothing is minted" is stated.
8. **Proof file mismatches (claim 7): as expected.** `sha256sum -c PROOF.sha256` fails on exactly 7 files: README.md, llm.txt, savante.agentcard.json, savante.commitments.json, savante.persona, savante.thot.json and todo.md. That list is exactly the set the branch changed (`git diff --stat main..generation-8`). Every other file passes.

**RATIONALE**

The binding is sound. The digests are reproduced from raw bytes, the binder reproduces the branch's output exactly, the generation 7 parent verifies offline, the doctrine root is unchanged, and no pin, mint, wallet or new version is claimed. What falls short is where the evidence lives. Every mindX fact the new persona text cites exists only in an uncommitted mindX working tree, and the mirror md5 the ledger records has no committed counterpart. Publishing this branch would tie a public record to evidence no reader can check. The statement about which model carries the seat is also stated unconditionally, but it holds for one model mode only.

**CONDITIONS**

1. The three mindX paths are committed before `generation-8` is pushed. Check: `git -C /home/hacker/mindX status --short daio/agents/agent_map.json daio/governance/boardroom.py mindx/godel/mindxtrain/personas/savante.persona` prints nothing, and `git -C /home/hacker/mindX show HEAD:mindx/godel/mindxtrain/personas/savante.persona | md5sum` prints `a7df3f9293e2d3d15d2f16af3384923c`.
2. README ("The seat runs on the carrier graded APPROVE_WITH_CONDITIONS") and todo.md ("The boardroom seat runs on the second") are limited to cloud/auto mode, and each names qwen3:1.7b as the local-mode model, not carrier-tested. Check: both files contain the string `qwen3:1.7b` beside the seat sentence.
3. PROOF.md and PROOF.sha256 are regenerated from the reviewed tree 8dcd05b. Check: `sha256sum -c PROOF.sha256` reports zero FAILED lines, and PROOF.md names 8dcd05b (or the commit that adds the proof files on top of it).
4. No document claims the seat has voted or held a session until `data/governance/boardroom_sessions.jsonl` on production holds a session with a `savante_sagi` vote. Check: `grep -c savante_sagi` on that file is at least 1 before any such claim appears.

**RISKS WATCHED**

- **The control carrier DEFERs too often, and DEFER now has force.** The approved carrier's own recorded failure is that it "DEFERs claims that evidence can decide". Every such DEFER now halts a session that would otherwise proceed and pages the operator. The rate of `deferred` outcomes against sessions whose evidence was complete is the measure to watch.
- **The seat depends on a cloud model that has not been measured on this box.** The graded carrier is `gpt-oss:120b-cloud`, which runs on Ollama Cloud's free tier (1 concurrent model, 500 requests a week), not the one-VPS baseline. The local model that would stand in for it, qwen3:1.7b, has no carrier test. The deciding experiment is the sagi probe set run on qwen3:1.7b.
