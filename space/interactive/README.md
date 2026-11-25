---
title: Savante
emoji: ⚖️
colorFrom: yellow
colorTo: gray
sdk: static
pinned: false
license: mit
hf_oauth: true
hf_oauth_expiration_minutes: 480
hf_oauth_scopes:
- inference-api
short_description: Savante, interactive — in your browser, with bankML
custom_headers:
  cross-origin-embedder-policy: credentialless
  cross-origin-opener-policy: same-origin
  cross-origin-resource-policy: cross-origin
thumbnail: https://huggingface.co/spaces/Gregory-L/Savante/resolve/main/gfx/Savante3-gen2-og.jpg
tags:
- sagi
- savante
- cryptoagi
- oversight
- webassembly
- browser-inference
models:
- prism-ml/Bonsai-1.7B-gguf
---

# Savante — the oversight office, interactive edition

<img src="https://huggingface.co/spaces/Gregory-L/Savante/resolve/main/gfx/Savante3.png" alt="Savante, the bust" width="240" align="right">

**savante_sagi · the prototype sAGI · Savante knows.** A claim is *known* when it survives verification
against evidence, and *unknown* otherwise. There is no third state.

Canon: [cryptoAGI/savante](https://github.com/cryptoAGI/savante) · engine: [cryptoAGI/sagi](https://github.com/cryptoAGI/sagi).

A **static** Space: no server, no compute of its own, and no key of anyone's. Everything runs in your browser.

**This is the interactive edition.** It is [PYTHAI/savante](https://huggingface.co/spaces/PYTHAI/savante), the template
and the public edition, with three additions:

- **The page opens on Savante.** The bust and the introduction come first, then the field. From her first answer, the
  bust becomes a mini aivatar in the head of each response window, and it pulses while she answers.
- **Savante in your browser.** [bankML](https://github.com/cryptoAGI/bankml)'s own engine, compiled to WebAssembly
  (browseML, from [PYTHAI/bankml](https://huggingface.co/spaces/PYTHAI/bankml)), runs her persona on your CPU.
  - The model, Bonsai-1.7B 1-bit (248 MB), is downloaded once and kept in your browser.
  - bankML checks its sha256 before she answers, and puts a receipt on every answer.
  - Nothing is sent anywhere, and nothing is published.
- **The ultimate input field.** It is the input/response field from
  [ultimate-bankml-ui](https://huggingface.co/spaces/PYTHAI/ultimate-bankml-ui).
  - Each answer opens in a response window that you can move, resize from any corner, pop out to another screen, and
    call home.
  - **Three modes.** **sAGI** is Savante mode, where the page starts: she answers as herself, and the field carries
    her button set (carrier, load, example, verdict, integrity). **>** is the generic mode: a plain assistant on the
    same carrier. **T** is terminal mode: `sagi`, `carrier`, `load`, `integrity`, `hub`, `tokens`, `temp`, `last`,
    `details`, and every field command (`help`).
  - **Docking.** Drag the field near any screen edge and it docks there by magnetic attraction. Drag its grip to
    pull it free.
- **The answer, not the paperwork.** How each answer was delivered (tokens, speed, carrier, clock, receipt) is
  shown under it only if you choose "show delivery details" (Responses menu, or `details on`). Either way it is
  kept in **.memory** as a delivery record (⏱): the same fields as Savante's improve.skill `.memory` (question,
  answer, carrier, deliveries, finish, limit, usage, timings, response_sha256), never sent to the model. It is
  also in the T-mode log (`last`).
- **The count in EVM units.** The improve.skill count also reads as a fixed-point number with 18 decimals: 1 in the
  count is the smallest unit (0.000000000000000001, like one wei), so iteration 20 reads 0.000000000000000020.

| room | what it does |
|---|---|
| **Ask Savante** | Talk to the office through the ultimate input field. You choose who carries her: <ul><li>**bankML in this browser**: free, with a receipt.</li><li>**Bonsai on the free public CPU** of the mindXhfgradio Space: free. Your question and her answer are published in the improve.skill loop, [PYTHAI/savante-loop](https://huggingface.co/datasets/PYTHAI/savante-loop).</li><li>**Bonsai on your own machine**, through llama-server.</li><li>**A Hugging Face Inference Provider**: sign in, and the call uses your token and your quota.</li></ul> |
| **Faicey** | the office embodied. The controls sit on the left, which is the machine with the skin off; the right is the human half of the bust. The **mouth is an oscilloscope** of the audio playing (voaicey, persona `savante`), the **eye is your camera** and the **ear is your microphone**. These are opt-in, stay in your browser, and stop when you leave the room. It's a render, not a measurement: faceprint and voiceprint stay null. |
| **PYTHAI** | [huggingface.co/PYTHAI](https://huggingface.co/PYTHAI) read from your browser: every model, dataset and Space, and whether each mirror of this office carries canon main. Public GETs only, with no write path. |
| **Hub** | Hugging Face as a tool: a timestamped reading of a model repository — commit sha, licence, task, parameters, live inference providers. A reading is evidence of what the Hub said, not a verdict on the model. |
| **The Office** | the charter read from `savante.persona`: mantra, oath, beliefs, verdicts, mint status. |
| **Verdict** | the five-field contract. It refuses to render APPROVE with no findings recorded. |
| **Integrity** | your browser hashes every artefact the ledger commits to (sha256 + CIDv1) and compares with `savante.commitments.json`. Disagreement is shown, not hidden. |
| **Skills** | Savante's own `/sagi` skill, a public edition of the Hugging Face skill, the prompt and `llm.txt`, verbatim. |

## Deliberately absent

- **No shell and no server.** The desktop edition can execute read-only verification commands; a public page never can.
- **No host token.** Nothing a visitor does spends the owner's account.
- **No server for browseML.** Its answers never leave the visitor's browser, and they are not counted in the public loop.
- **No mint button.** Savante is not minted; `iNFT.md` renders `VERDICT: DEFER` on binding the office to a token.

## Honest labels

- A model's answer is a **draft**, never a finding.
- The bundled canon is whatever `MIRROR.json` names. This page is canon too, as `space/interactive/` in
  cryptoAGI/savante. Its build bundles (uif-space, browseML wasm) are not canon; they are built by ultimate-bankml-ui and bankML. **Integrity should show every artefact agreeing**. If it ever shows a disagreement, believe it over this line.
- Hugging Face now requires a paid plan to host Gradio Spaces, so this edition is static. The Gradio edition
  (with MCP tools) is in the canon as `ui.py`.
- **The bust is the artwork the operator named** (`gfx/Savante3.png`, sha256 `30a59db4…c5a9a8`, recorded in the
  generation-7 ledger). It is not pinned and nothing is minted, so the card's `image` is null. Every image of
  Savante, and `PROOF.md` with the digests of the skill and every file that carries a proof, are in the canon.
- **Two pages, one canon.** The canon files (`canon/`, `skills/`, `gfx/`) are the same as at
  [PYTHAI/savante](https://huggingface.co/spaces/PYTHAI/savante); only the page differs. Neither
  page is authoritative: [cryptoAGI/savante](https://github.com/cryptoAGI/savante) is the canon, and if a page
  and the canon ever differ, the canon wins — which is what **Integrity** lets you check for yourself.
- sAGI **v0.0.5** · MIT.
