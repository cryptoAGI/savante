---
name: huggingface
description: >
  Hugging Face as a tool for a chartered officer — reading the Hub as evidence (model cards, licences,
  sizes, live inference providers), Spaces and ZeroGPU rules, OAuth so visitors spend their own quota,
  MCP, and the traps that cost real debugging time. Public edition of the mindX house skill: the
  operational internals (credential storage, private repositories, node deploy state) are removed.
  Triggers: "huggingface", "HF", "Hub", "ZeroGPU", "Space", "Gradio", "inference provider", "licence".
---

# Hugging Face, read as evidence

The Hub is a source of **readings**, not of truth about a model. A model card says what its authors
claim; a licence file says what they grant; a provider mapping says who serves it *today*. An officer
records each reading with the time it was taken, and never promotes a reading into a verdict on
quality, safety or fitness — those need a measurement.

## Readings an officer may take (no token required for public repos)

| question | reading | caveat |
|---|---|---|
| What licence governs it? | the `license` tag, then the `LICENSE` file itself | a tag of `other` means *read the file*; tags and files can disagree |
| How big is it? | safetensors parameter count and total file size | FP8 / compressed checkpoints differ from BF16 by roughly 2× in bytes |
| Who serves it right now? | the inference-provider mapping (`live` / `staging`) | mappings change without notice; re-read on the day you depend on it |
| What does it do? | `pipeline_tag`, architecture, `custom_code` | `custom_code` means running the authors' Python — review it first |
| Is it popular? | downloads, likes | popularity is not a measurement of correctness |

In Python, read-only: `HfApi().model_info(repo_id, expand=["inferenceProviderMapping", "safetensors", "cardData"])`.

## Forking a model repository

- There is **no server-side cross-repo copy** for model weights: duplicating a repository means
  downloading and re-uploading every byte. A 1T-parameter checkpoint is hundreds of gigabytes — price
  the bandwidth, the disk and the storage quota *before* starting.
- Record, alongside the fork: the source repo id, the **source commit sha**, the licence file as it
  read on the day, and why the fork exists. A fork without its source commit is a copy nobody can audit.
- Licences change between releases of the same family. A fork preserves the licence of the commit it
  was taken from — so take the commit, not "latest".

## Spaces

- Gradio Spaces accept `hf_oauth: true` in the README. With `hf_oauth_scopes: [inference-api]` a
  signed-in visitor's token can call Inference Providers, so **the visitor pays**, not the Space owner.
  Never place an owner token in a public Space.
- Free CPU Spaces sleep after about 48 hours idle; the first request after sleep is a cold start.
- `short_description` in the README must be **60 characters or fewer**, or the upload is rejected.
- Only **public or protected** Spaces can be embedded (`<gradio-app src="https://<ns>-<name>.hf.space">`).
- `demo.launch(mcp_server=True)` exposes each function with a docstring as an MCP tool; every Gradio
  Space also publishes `https://huggingface.co/spaces/<ns>/<name>/agents.md`.

## ZeroGPU

- Quota belongs to the **caller**: anonymous ≈ 2 min/day, free ≈ 5, PRO ≈ 40. A free personal account
  hosts **2** ZeroGPU Spaces; a free organization cannot host one (HTTP 402).
- The Hub checks ZeroGPU quota **before** existence: `create_repo(..., space_hardware="zero-a10g",
  exist_ok=True)` on an existing Space still returns 402 once the slots are used. Check `repo_exists` first.
- Detect ZeroGPU with the `SPACES_ZERO_GPU` environment variable. Load weights at module level; wrap the
  generate call in `@spaces.GPU(duration=callable)`, and the callable must accept every handler argument.

## Traps

- Gradio 6 moved `theme` / `css` to `launch()` and dropped `type=` from `Chatbot` / `ChatInterface`.
  Read the installed signature; never pin a major.
- `list_repo_tree()` entries carry `.path`; only `repo_info().siblings` carry `.rfilename`.
- Qwen3 post-trained models think out loud by default; send `/no_think` or strip `<think>` blocks
  before showing an answer.

*Knowledge is what survives verification; nothing else counts — a Hub reading included.*
