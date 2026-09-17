# gfx — the images of Savante

Collected 2026-09-16 at the operator's request, and published here by the operator's decision. The instructions,
in the Claude Code session named by the `Claude-Session:` trailer of the commit that added this folder, were
"collect all images of Savante while at it store in savante/gfx" and "push as next incremental version"; this
repository is public, so storing the images here and pushing them is publishing them. Two of the ten
(`Savante-concept-sheet.jpeg`, `sAGIiNFT.jpeg`) came from a folder that is not under version control, so this
repository is now their only versioned copy.

Every file is kept byte for byte as found; nothing was re-encoded or stripped. None carries EXIF, XMP, GPS or a
host path (checked with `strings` for exif, xmp, http, gps and host paths). One carries other embedded data:
`sAGIiNFT.jpeg` has an ICC colour profile, which describes colour and nothing about where the file came from.

**The artwork is `Savante3.png`, the bust.** The operator named it on 2026-09-16 ("use the Savante bust for the
image of Savante" and "yes, use Savante3"), in the Claude Code session named by the `Claude-Session:` trailer of
the commit that added this folder. Generation 7's `savante.commitments.json` records its sha256 under
`image_candidate`. That settles the naming half of `iNFT.md` condition 4. The pin half is open: nothing here is
pinned, so the card's `image` is null and every CID below is **predicted**, not a pin.

Check any file: `sha256sum gfx/<file>` must print the digest in its row (all ten are also in `../PROOF.sha256`).

## Two things a reader should not assume

- **The `.png` files are JPEG bytes.** All four begin `ff d8 ff e0`, the JPEG signature. The names are the
  operator's and are kept, because the hash names the bytes and not the extension. A minter should declare
  `image/jpeg` for `Savante3.png`, not `image/png`.
- **A predicted CID is not a pin.** Each CID below is CIDv1 raw (codec 0x55, sha2-256) over the whole file,
  computed by `bind/savante_bind.py`'s `cid_or_none`. Every file is under the 256 KiB single-block bound, so an
  IPFS node adding it with `--cid-version 1 --raw-leaves` should return the same CID. Condition 4 still takes
  only the CID the node returns.

## The files

| file | bytes | pixels, format | sha256 | CIDv1 raw (predicted) | what it shows | collected from |
|---|---:|---|---|---|---|---|
| `Savante3.png` | 154,668 | 1024x1536 JPEG | `30a59db4ce76dbea8b6a97c143a74996c3c1cd317e3af21f6a18757ae8c5a9a8` | `bafkreibquwo3jttw3pviw2uxyfb2osmwypa42ml6hlzb62qyov5orrnjva` | **The artwork (named by the operator, 2026-09-16).** The bust: head and shoulders, cyborg, blue eyes, city lights behind. | mindX `gfx/Savante3.png` |
| `Savante1.jpeg` | 119,034 | 1024x1536 JPEG | `356b0045cb66ed78a1979b1c8eaabde065941793b8def27baef8ec12b9842425` | `bafkreibvnmaels3g5v4kdf43dshkvppamwkbpe5y33zhxlxy5qjltbbeeu` | The bust as in `Savante3.png` to the eye, a different encoding (different bytes, different hash). Not the named artwork. | mindX `gfx/Savante1.jpeg`, also in the AgenticPlace gfx folder |
| `Savante.png` | 168,059 | 1024x1536 JPEG | `dee70d2af7889789f7645eb1cdca9812e1d284211e47e3fda03852161e3a7082` | `bafkreig644gsv54is6e7ozc6whg4vgas4hjiiii6i7r73ibykilb4otqqi` | Full figure from behind, looking over the shoulder, city lights. | mindX `gfx/Savante.png` |
| `Savante2.png` | 161,071 | 1024x1536 JPEG | `701bf6d626d6c748a0af49612f0acde458005d8f4be0ed7748cd5cd976ce2a85` | `bafkreidqdp3nmjwwy5ekbl2jmexqvtpelaaf3d2l4dwxosgnltmxntrkqu` | Full figure from behind, second variant. | mindX `gfx/Savante2.png` |
| `Savante-agenticplace.jpeg` | 122,742 | 1024x1536 JPEG | `f6f7248fd5e5c0439498c9c87e0a002a144fe74b94f86fd62ad4c8d7b07328c8` | `bafkreihw64si7vpfybbzjggjzb7auabkcrh6os4u7bx5mkwuzdl3a4ziza` | Full figure from behind, the variant kept in the AgenticPlace gfx folder (same pose family as `Savante.png`). | AgenticPlace `gfx/Savante.jpeg`, renamed here to avoid a name clash |
| `Savante-concept-sheet.jpeg` | 56,036 | 1402x1122 JPEG | `7a39b170707803078bcec78d85e3d7ece9d2de0643405396b9670468bcc0332f` | `bafkreid2hgyxa4dyamdyxtwhrwc6hv7m5hjn4bsdibjznolharulzqbtf4` | An earlier character concept sheet (a human research analyst named Savante), before the cyborg design. | PYTHAI `gfx/Savante.jpeg`, renamed here to avoid a name clash |
| `sAGIiNFT.jpeg` | 104,084 | 896x1280 JPEG | `0b345e19cdd37b01eaf4ff41d9bbfb490bf5c8c50b14d957bd6aa5e7d10f55bb` | `bafkreialgrpbttotpma6v5h7ihm3x62jbp24rrilctmvpplkuxt5cd2vxm` | "Edition II — Savante: Attestor": the sAGI iNFT concept, a hooded figure with a hash cube and a verification ring. | PYTHAI `gfx/sAGIiNFT.jpeg` |
| `mindXcodephreaksavante.png` | 215,914 | 1536x1024 JPEG | `9f15a93026f3ed79a0a99f33e1a4da263fbd9c4f36accc78522a6a36e71b4305` | `bafkreie7cwutajxt5v42bkm7gpq2jwrgh66zytzwvtghqurkni3oog2dau` | Promotional banner: Professor Codephreak and a figure captioned PYTHAI on either side of mindX. The file name says savante; the image's own caption says PYTHAI. | mindX `gfx/mindXcodephreaksavante.png` |
| `Savante3-gen2-landscape.jpg` | 98,096 | 1024x576 JPEG | `8d7328b2f0958e5223aff036d2cbbbd471543e1fdd879f883117c48dcd863ab9` | `bafkreienomulf4evrzjchl7qg3jmxo6uofkd4h65q6pyqmixysg43br2xe` | Landscape crop of the bust, made for the generation-2 announcement. | the mindX production node's `gfx/jpg/` |
| `Savante3-gen2-og.jpg` | 119,290 | 1200x628 JPEG | `9a16ea3db95ad2f9247cb8147d32e61efb9953dd6181cf48cc05a2f39a20dd5f` | `bafkreie2c3vd3ok22l4si7fycr6tfzq67omvhxlbqhhurtafulzzuig5l4` | 1200x628 social card of the bust: the featured image of the generation-2 announcement on rage.pythai.net (post 1509, media 1512). | the mindX production node's `gfx/jpg/` |

## Held back

Twelve more files had Savante or sAGI in their names: screen captures of Claude Code sessions (2026-06-30 to
2026-09-14). They are not in this public repository, because they show host paths, private repository names,
deployment commands and browser bookmarks. They are held back, not lost: the operator still has them.
