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
short_description: Savante — the read-only office of sAGI
thumbnail: https://huggingface.co/spaces/PYTHAI/savante/resolve/main/gfx/Savante3-gen2-og.jpg
tags:
- sagi
- savante
- cryptoagi
- oversight
---

# Savante — the oversight office, public edition

<img src="https://huggingface.co/spaces/PYTHAI/savante/resolve/main/gfx/Savante3.png" alt="Savante, the bust" width="240" align="right">

**savante_sagi · the prototype sAGI · Savante knows.** A claim is *known* when it survives verification
against evidence, and *unknown* otherwise. There is no third state.

Canon: [cryptoAGI/savante](https://github.com/cryptoAGI/savante) · engine: [cryptoAGI/sagi](https://github.com/cryptoAGI/sagi).

A **static** Space: no server, no compute of its own, and no key of anyone's. Everything runs in your browser.

| room | what it does |
|---|---|
| **Ask Savante** | talk to the office. **`Qwen/Qwen3-8B`** answers by default, through Hugging Face Inference Providers, under [`Savante.prompt`](Savante.prompt). **Sign in with Hugging Face** — the call is made from your browser with *your* token and billed to *your* inference quota. |
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
- **No mint button.** Savante is not minted; `iNFT.md` renders `VERDICT: DEFER` on binding the office to a token.

## Honest labels

- A model's answer is a **draft**, never a finding.
- The bundled canon is whatever `MIRROR.json` names. The page itself is canon now (`space/` in
  cryptoAGI/savante), so the page and the canon change together. **Integrity should show every artefact agreeing**, and the
  PYTHAI room shows whether this mirror carries canon main. If it ever shows a disagreement, believe it over this line.
- Hugging Face now requires a paid plan to host Gradio Spaces, so this edition is static. The Gradio edition
  (with MCP tools) is in the canon as `ui.py`.
- **The bust is the artwork the operator named** (`gfx/Savante3.png`, sha256 `30a59db4…c5a9a8`, recorded in the
  generation-7 ledger). It is not pinned and nothing is minted, so the card's `image` is null. Every image of
  Savante, and `PROOF.md` with the digests of the skill and every file that carries a proof, are in the canon.
- **Two pages, one canon.** These same files are also served at
  [Gregory-L/Savante](https://huggingface.co/spaces/Gregory-L/Savante), the office's first public page. Neither
  page is authoritative: [cryptoAGI/savante](https://github.com/cryptoAGI/savante) is the canon, and if a page
  and the canon ever differ, the canon wins — which is what **Integrity** lets you check for yourself.
- sAGI **v0.0.5** · MIT.
