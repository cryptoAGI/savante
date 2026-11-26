#!/usr/bin/env python3
"""space/serve.py — lay the canon out the way the Hugging Face Spaces serve it, and serve it on this machine.

    python3 space/serve.py                 # http://127.0.0.1:7864/   (#faicey, #pythai open a room directly)
    python3 space/serve.py --layout DIR    # only write the layout into DIR (what the mirror sync uploads)
    python3 space/serve.py --edition interactive [--bundles DIR]
                                           # the interactive edition (Gregory-L/Savante): space/interactive/ over
                                           # the shared modules; its build bundles are not canon (see BUNDLES)

The page files are canon now (this directory). The canon artefacts the page reads are laid beside them under
the same paths the mirror sync uses: canon/<file>, canon/claude/... (a static host may refuse to serve a
dot-directory, so .claude/ becomes claude/ — the only renaming, and savante.js knows it), skills/sagi/SKILL.md
and gfx/. Stdlib only. It binds to 127.0.0.1 by default: the camera eye and the microphone ear need a secure
context, which a browser grants to localhost and to https, not to a LAN address over http.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import json
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Kept identical to mindX scripts/sync_savante_hf.py (SPACE_CANON, SPACE_RENAMED, SPACE_EXTRA).
SPACE_CANON = [
    "LICENSE", "llm.txt", "sAGI.agent", "sAGI.faice", "sAGI.model", "sAGI.prompt", "sAGI.tool",
    "sAGI.voaice", "savante.agentcard.json", "savante.commitments.json", "savante.persona",
    "savante.thot.json",
]
SPACE_RENAMED = {
    ".claude/agents/savante.md": "canon/claude/agents/savante.md",
    ".claude/skills/sagi/SKILL.md": "canon/claude/skills/sagi/SKILL.md",
}
SPACE_EXTRA = {".claude/skills/sagi/SKILL.md": "skills/sagi/SKILL.md",
               "gfx/Savante3.png": "gfx/Savante3.png",
               "gfx/Savante3-gen2-og.jpg": "gfx/Savante3-gen2-og.jpg"}
NOT_PAGE = {"serve.py", "__pycache__"}
EDITIONS = ("public", "interactive")
# The interactive edition's own files live in space/interactive/ and replace the public edition's same-named files.
# These build outputs are NOT canon: uif-space.* is built by ultimate-bankml-ui, the wasm by bankML (PYTHAI/bankml).
# They live on the Gregory-L/Savante Space only, the mirror sync never touches them, and here they are linked from
# --bundles DIR when given (without them the page loads, but the input field and in-browser carrier do not mount).
FORK = "browseML/Bonsai-1.7B-Q1_0.gguf.FORK.json"     # the browser model's pin (bankML's), which savanteML verifies against
BUNDLES = ["uif-space.js", "uif-space.css", "browseml.wasm", "browseml-mt.wasm", "browseml-mt-relaxed.wasm", FORK]
# Both editions carry savanteML (Savante in the browser) and the input field, so both take every bundle. Uploaded to
# each Space beside the page, never by the mirror sync.
PUBLIC_BUNDLES = BUNDLES
# The host edition: the page served by a dmind host itself (mindX at /savante/), so the cluster room may send the
# realm token to the host's own same-origin paths. savante-host.json names them, as browseML's browseml-host.json does.
HOST_JSON = {"label": "mindX", "share": {
    "join": "/sharedcpu/join", "update": "/sharedcpu/update", "pull": "/sharedcpu/pull", "result": "/sharedcpu/result",
    "leave": "/sharedcpu/leave", "me": "/sharedcpu/me", "collect": "/sharedcpu/collect", "insight": "/insight/sharedcpu",
    "token": "mindx_realm_token", "signin": "/activity?from=/savante/office/%23cluster"}}


def page_files(edition: str = "public") -> list[tuple[Path, str]]:
    """(source, served path) for every file of the page: the shared files of space/, with an edition's own
    files laid over them. The public edition is space/ minus space/interactive/."""
    shared = {p.relative_to(HERE).as_posix(): p for p in HERE.rglob("*")
              if p.is_file() and not (set(p.relative_to(HERE).parts) & NOT_PAGE)
              and p.relative_to(HERE).parts[0] != "interactive"}
    if edition == "interactive":
        own = HERE / "interactive"
        shared.update({p.relative_to(own).as_posix(): p for p in own.rglob("*") if p.is_file()})
    return sorted((src, rel) for rel, src in shared.items())


def layout(dest: Path, link: bool = False, edition: str = "public", bundles: Path | None = None,
           host_edition: bool = False) -> Path:
    """Copy (for upload) or symlink (for serving here, so an edit shows on reload) the Space layout into dest."""
    dest.mkdir(parents=True, exist_ok=True)
    pairs = page_files(edition)
    if bundles:
        pairs += [(bundles / b, b) for b in (BUNDLES if edition == "interactive" else PUBLIC_BUNDLES) if (bundles / b).is_file()]
    pairs += [(ROOT / f, f"canon/{f}") for f in SPACE_CANON]
    # two maps, iterated separately: they share a source (.claude/skills/sagi/SKILL.md goes to two places), so a
    # merged dict would keep only one of its destinations
    pairs += [(ROOT / s, d) for s, d in SPACE_RENAMED.items()]
    pairs += [(ROOT / s, d) for s, d in SPACE_EXTRA.items()]
    if host_edition:
        (dest / "savante-host.json").write_text(json.dumps(HOST_JSON, indent=1) + "\n", encoding="utf-8")
    for src, rel in pairs:
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if link:
            out.unlink(missing_ok=True)
            out.symlink_to(src.resolve())
        else:
            shutil.copyfile(src, out)
    return dest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7864)
    ap.add_argument("--layout", type=Path, help="write the layout into this directory and exit")
    ap.add_argument("--edition", choices=EDITIONS, default="public")
    ap.add_argument("--bundles", type=Path, help="a directory holding the non-canon BUNDLES")
    ap.add_argument("--host-edition", action="store_true",
                    help="write savante-host.json: the copy a dmind host serves itself (the cluster may contribute)")
    a = ap.parse_args()
    if a.layout:
        print(layout(a.layout, edition=a.edition, bundles=a.bundles, host_edition=a.host_edition))
        return
    d = layout(Path(tempfile.mkdtemp(prefix="savante-space-")), link=True, edition=a.edition, bundles=a.bundles,
               host_edition=a.host_edition)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(d))
    print(f"Savante ({a.edition} edition), served from {d}: http://{a.host}:{a.port}/   (#faicey · #pythai)")
    http.server.ThreadingHTTPServer((a.host, a.port), handler).serve_forever()


if __name__ == "__main__":
    main()
