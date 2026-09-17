# PROOF — Savante, sAGI v0.0.5, generation 7

The digests of the sAGI skill and of every file in this repository that carries a proof: the office, its
bound ledger, the artwork, the verdict records and the tools that check them. Written from the tree of the
commit that adds this file, whose parent is `e95a135`. Every value here can be recomputed by anyone
holding a clone; none is taken on trust.

## Check it

```sh
sha256sum -c PROOF.sha256          # every tracked file except PROOF.md and PROOF.sha256
python3 bind/savante_verify.py .   # recompute the ledger: digests, doctrine root, bundle root, card
```

`PROOF.sha256` is reproducible with
`git ls-files -z ':!PROOF.md' ':!PROOF.sha256' | LC_ALL=C sort -z | xargs -0 sha256sum`.
The CIDs are CIDv1 raw (codec 0x55, sha2-256, base32), computed by `bind/savante_bind.py`'s `cid_or_none` over
the whole file. Every file here is under the 256 KiB single-block bound, so every one has a CID. They are
**predicted** CIDs: nothing is pinned.

## The roots

| root | value | what it answers |
|---|---|---|
| doctrine root | `0x92fe83eb0fb8fb6b9cbde75ee4bbb671032a849ee25d65592b86913d0ae137d0` | is the office still the office? (keccak256 over the persona's 15 doctrine clauses; unchanged since generation 2) |
| bundle root | `0x144550cedc18d2c126489fbbb0500d67fddf92f9f009d45a9b9ff67c58fe2b96` | is this the same facet bundle? |
| THOT identity | `bafkreiebawdkwxhfefnizz32jflqpjzju4r444j7msky6pluyynnirsrmq` | the name of generation 7 (parent `bafkreibzx5apnrk5prim4g5in6vsaqwoztvfc7jfny4hwdhb65g7pmzr44`) |
| identity contentRoot | `0xd0dfb05db1516bcea6c6e9d3c1be2a7b342ad01bc59bd7b8f0d0ee2ac49b7210` | the same identity as a keccak256 slot value |
| card | `bafkreicx2bh4vl3zahiygebn35ntqjkpece7dpuk76npnkduknj56xguom` | the public card as written (keccak256 canonical `0x8d4cc9e211aded279f5cacb41b2a6987652e00e63a4c46209b7d7400511e4971`) |
| verdict record 1 | `bafkreibke7n3v5ykztl4xpyltf4grhslddpcl3diwavrqpibbh3onqmdhi` | `record_cid`, recomputed from the record with `record_cid` set to null |
| ledger's commit | `30d1e8c88435c4b2182cf1301e1cb865466cdb42` | the commit the ledger hashes (`components_differing_from_head` is `[]`) |

## The artwork

`gfx/Savante3.png`: 154,668 bytes, sha256 `30a59db4ce76dbea8b6a97c143a74996c3c1cd317e3af21f6a18757ae8c5a9a8`, predicted CID `bafkreibquwo3jttw3pviw2uxyfb2osmwypa42ml6hlzb62qyov5orrnjva`. The ledger records it
under `image_candidate.named_by_operator`. The file is JPEG bytes under a `.png` name. Not pinned, so the card's
`image` is null. The other nine images of Savante are in `PROOF.sha256` and indexed in `gfx/README.md`.


## The skill

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `.claude/skills/sagi/SKILL.md` | sAGI skill, v0.0.5 | 10,325 | `b8b9b62db9bac8286171a5766fe23f0512987872d2cefc9598036b7609daff30` | `bafkreifyxg3c3on2zaugc4nfozx6epyfckmhq4wsz36jlgadnn3atwx7ga` |

## The office: charter, identity and facets (bound in the ledger)

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `.claude/agents/savante.md` | charter (operative) | 7,122 | `2cf2d3b6a42c9438f89c6dc3bae833486e356795a997e8a0f932205d2fe18c3a` | `bafkreibm6lj3njbmsq4prhdnyo5oqm2iny2wpfnjs7ukb6jsebos7ymmhi` |
| `savante.persona` | identity: the .persona | 51,237 | `fd1933f2dc636a818744edaeade6454e329fddb5438d2ad264e331fd9cc808d3` | `bafkreih5dez7fxddnkayorhnv2w6mrkogkp53nkdruvnezhdgh6zzsai2m` |
| `sAGI.agent` | facet: agent class | 5,461 | `e5a8b0111b3b3d342d5f01057c019044bca46a592ee18ca1ec1e031c4263a650` | `bafkreihfvcybcgz3hu2c2xybav6adecexssguwjo4ggkd3a6amoeey5gka` |
| `sAGI.model` | facet: model (pins none) | 1,636 | `03dbbf5069cfdbcd67747eff1a513217b8139e16e0b4cc74aa71015adb9d3581` | `bafkreiad3o7va2op3pgwo5d674nfcmqxxajz4fxawtghjktrafnnxhjvqe` |
| `sAGI.prompt` | facet: charter body as prompt | 7,191 | `baf5a302bf591b977d45ff21c484cc1279c9693e0f65ae9541db42c042bdcffe` | `bafkreif26wrqfp2zdolx2rp7ehcijtasphewspqpmwxjkqo3ilaefpop7y` |
| `sAGI.tool` | facet: tool allowlist | 3,769 | `ebd3ec9342801ae3dc72840db55e7052b33ff487b6b1fa2e3145e69d9da9ece4` | `bafkreihl2pwjgquadlr5y4uebw2v44cswm77jb5wwh5c4mkf42oz3kpm4q` |
| `sAGI.voaice` | facet: voice | 1,775 | `d4619d4c6fcf0913ed0e2a1616eb219d2bff9a22efbb323a7e579cf44e25862e` | `bafkreigumgouy36pbej62drkcylowim5fp7zuixpxmzdu7sxtt2e4jmgfy` |
| `sAGI.faice` | facet: face | 1,866 | `6e2d33f8e6ad06e56c254549020643ab70b55cb61a6cb0328751ba33b7e3991f` | `bafkreidofuz7rzvna3swyjkfjebamq5loc2vznq2nsydfb2rxiz3py4zd4` |

## Derived by the binder (never hand-edited)

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `savante.agentcard.json` | public card: EIP-721 metadata + ERC-8004 registration | 7,815 | `57d04fcaaf7901d183102ddf5b38254f2089f1be8aff9af6a8745353df5cd473` | `bafkreicx2bh4vl3zahiygebn35ntqjkpece7dpuk76npnkduknj56xguom` |
| `savante.commitments.json` | integrity ledger | 17,452 | `80821b8ada201b278b4d9148d26d80667e5802d44f151ce2a647bec4a4fd1ab1` | `bafkreieaqinyvwradmtywtmrjdjg3adgpzmafvcpcuoofjshx3ckj7i2we` |
| `savante.thot.json` | THOT manifest, generation 7 | 9,090 | `727309a72809e77270896ed825e8a85818df1257bac4a15ac477c5b6da834bf9` | `bafkreidsome2okaj45zhbclo3as6rkcyddprev52ysqvvrdxyw3nva2l7e` |

## The artwork

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `gfx/Savante3.png` | the bust, named by the operator | 154,668 | `30a59db4ce76dbea8b6a97c143a74996c3c1cd317e3af21f6a18757ae8c5a9a8` | `bafkreibquwo3jttw3pviw2uxyfb2osmwypa42ml6hlzb62qyov5orrnjva` |

## Evidence records

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `verdicts/record-0001.json` | verdict record 1 | 15,406 | `d54f380a54e2a0156140455bd0fe9dc26fe369e0385f536dd7192a58a78d391e` | `bafkreigvj44auvhcuakwcqcflpip5hocn7rwtybyl5jw3vyzfjmkpdjzdy` |
| `bind/verdict_record.schema.json` | verdict record schema | 6,577 | `70f191cf666e3ff5d91df600271c4f9916b98e3d1ee33ec9129ed412df522fb9` | `bafkreidq6gi46ztoh725shpwaatryt4zc24y4pi64m7mseu62qjn6urpxe` |
| `ci/gate-runs/0001/verdict.md` | CI gate run 0001 | 7,633 | `4c980486d15e249728beff4ff2f7e29ec1c714ebe2d3cbd32b6aad1c7e61d0da` | `bafkreicmtacinuk6eslsrpx7j7zppyu6yhdrj27c2pf5gk3kvuoh4yoq3i` |
| `ci/gate-runs/0002/verdict.md` | CI gate run 0002 | 8,564 | `15abbccf1fff83aa76b76ebc16566a2188c1d972f43d5ab3868896a613dc8e29` | `bafkreiavvo6m6h77qovhnn3oxqlfm2rbrda5s4xuhvnlhbuis2tbhxeofe` |

## The tools that make and check the proofs

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `bind/savante_bind.py` | binder (operator's tool) | 93,653 | `0959a91decaf3a12bdf38231a15a7587d8b5f0711f1a8dcb3c01b09843896c1d` | `bafkreiajlgur33fphijl344cggqvu5mh3c27a4i7dkg4wpabwcmehclmdu` |
| `bind/savante_verify.py` | verifier (anyone's tool) | 63,480 | `fe7cdfb7bef42d43fed97df00b103575ae3779a094631201a34ebf5bcf9ae31b` | `bafkreih6ptp3ppxufvb75wl56afranlvvy3xtieummjadi2ox5n47gxddm` |

## Everything else

| file | bytes | sha256 | CID (predicted) |
|---|---:|---|---|
| `.gitignore` | 19 | `862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793` | `bafkreiegejr7uh2gyihq2hsnvrp7zr22xvk4baqrwlbymtc7q5sltwdxsm` |
| `LICENSE` | 1,091 | `3970382bf4f5fc6adaaff98835fbfd8a01bb1d3ec249b8ab07395e06b1363e3c` | `bafkreibzoa4cx5hv7rvnvl7zra27x7mkag5r2pwcjg4kwbzzlydlcnr6hq` |
| `MANIFESTO.md` | 7,186 | `4023714ef1226b0d8a646b3bfcd9d351db3310965101c71b43cf3ff18dce5726` | `bafkreicaenyu54jcnmgyuzdlhp6ntu2r3mzrbfsrahdrwq6ph7yy3tsxey` |
| `README.md` | 12,811 | `1335d7816f45137b21d2fc73e5a7f835bb81a393f67912e4f19dd1824ba4de4a` | `bafkreiatgxlyc32fcn5sdux4ops2p6bvxoa2he7wpejoj4m52gbexjg6ji` |
| `SAVANTE_AS_A_SERVICE.md` | 5,341 | `e401f81b895bcb67341610460f792689c8b90fbbde16dc52e0091e38eb8e4952` | `bafkreiheah4bxck3znttifqqiyhxsjujzc4q7o66c3offyajdy4oxdsjki` |
| `Savante.md` | 7,427 | `7a29ebc05085e23ff75a9144e22690b27988f3ac3fbeeddce5678b21ea2361ab` | `bafkreid2fhv4auef4i77owuritrcnefspgephlb7x3w5zzlhrmq6ui3bvm` |
| `bind/savante_publish.py` | 11,180 | `fe0162d26e416edb1ff068cf37ad905d466f1b78287538389095347574d08315` | `bafkreih6afrne3sbn3nr74diz4323ec5izxrw6biou4dreevgr2xjuedcu` |
| `ci/gate-runs/0001/meta.txt` | 1,665 | `3fdb410b95aaceb04a07143313cdddb00e4a052c82e65b26cb7991fe94ecaba7` | `bafkreib73naqxfnkz2yeubyugmj43xnqbzfaklec4znsns3zsh7jj3flu4` |
| `ci/gate-runs/0002/meta.txt` | 775 | `745c71d6b0bbdb02c5fbf5e3a0127b25438e96e86cbec67063e3ba98ef269973` | `bafkreidulry5nmf33mbml67v4oqbe6zfiohjn2dmx3dhay7dxkmo6juzom` |
| `ci/gate-runs/0003/meta.txt` | 950 | `c8d726b6501199a5a439cad3d5b9c8d6c89858cf88680773be9cf9dc32e4d178` | `bafkreigi24tlmuartgs2iook2pk3tsgwzcmfrt4inadxhpu47hodfzgrpa` |
| `ci/gate-runs/0003/verdict.md` | 2,906 | `6994f3d39836772d35b6cb81cb7828236b3bf31893c4c23f26ef265198ab7bf9` | `bafkreidjstz5hgbwo4wtlnwlqhfxqkbdnm57ggetytbd6jxpezizrk337e` |
| `explanation.md` | 7,175 | `311c7518416a9a0eadf53f3ac464689eb14304c73ec53dc7f9fb72f75132bf56` | `bafkreibrdr2rqqlktihk35j7hlcgi2e6wfbqjrz6yu64p6p3ol3vcmv7ky` |
| `gfx/README.md` | 6,086 | `c7269398ad4692dea22df3915dce8c08fdf253739bb11251e45934752720bc4d` | `bafkreighe2jzrlkgslpkelptsfo45dai7xzfg443wejfdzczgr2soif4ju` |
| `gfx/Savante-agenticplace.jpeg` | 122,742 | `f6f7248fd5e5c0439498c9c87e0a002a144fe74b94f86fd62ad4c8d7b07328c8` | `bafkreihw64si7vpfybbzjggjzb7auabkcrh6os4u7bx5mkwuzdl3a4ziza` |
| `gfx/Savante-concept-sheet.jpeg` | 56,036 | `7a39b170707803078bcec78d85e3d7ece9d2de0643405396b9670468bcc0332f` | `bafkreid2hgyxa4dyamdyxtwhrwc6hv7m5hjn4bsdibjznolharulzqbtf4` |
| `gfx/Savante.png` | 168,059 | `dee70d2af7889789f7645eb1cdca9812e1d284211e47e3fda03852161e3a7082` | `bafkreig644gsv54is6e7ozc6whg4vgas4hjiiii6i7r73ibykilb4otqqi` |
| `gfx/Savante1.jpeg` | 119,034 | `356b0045cb66ed78a1979b1c8eaabde065941793b8def27baef8ec12b9842425` | `bafkreibvnmaels3g5v4kdf43dshkvppamwkbpe5y33zhxlxy5qjltbbeeu` |
| `gfx/Savante2.png` | 161,071 | `701bf6d626d6c748a0af49612f0acde458005d8f4be0ed7748cd5cd976ce2a85` | `bafkreidqdp3nmjwwy5ekbl2jmexqvtpelaaf3d2l4dwxosgnltmxntrkqu` |
| `gfx/Savante3-gen2-landscape.jpg` | 98,096 | `8d7328b2f0958e5223aff036d2cbbbd471543e1fdd879f883117c48dcd863ab9` | `bafkreienomulf4evrzjchl7qg3jmxo6uofkd4h65q6pyqmixysg43br2xe` |
| `gfx/Savante3-gen2-og.jpg` | 119,290 | `9a16ea3db95ad2f9247cb8147d32e61efb9953dd6181cf48cc05a2f39a20dd5f` | `bafkreie2c3vd3ok22l4si7fycr6tfzq67omvhxlbqhhurtafulzzuig5l4` |
| `gfx/mindXcodephreaksavante.png` | 215,914 | `9f15a93026f3ed79a0a99f33e1a4da263fbd9c4f36accc78522a6a36e71b4305` | `bafkreie7cwutajxt5v42bkm7gpq2jwrgh66zytzwvtghqurkni3oog2dau` |
| `gfx/sAGIiNFT.jpeg` | 104,084 | `0b345e19cdd37b01eaf4ff41d9bbfb490bf5c8c50b14d957bd6aa5e7d10f55bb` | `bafkreialgrpbttotpma6v5h7ihm3x62jbp24rrilctmvpplkuxt5cd2vxm` |
| `iNFT.md` | 43,213 | `d42efa176a76b295e03388efb8c72c793f970ab0d5220387c6aa7c6307dc96f5` | `bafkreiguf35bo2twwkk6am4i564moldzh6lqvmgveibyprvkprrqpxew6u` |
| `llm.txt` | 10,034 | `81160a697a7e69757986ae491878e0a53e8276df390a2422fa0477e8da8bea5a` | `bafkreiebcyfgs6t6nf2xtbvojemhryffh2bhnxzzbiscf6qeo7unvc7kli` |
| `sAGI.md` | 6,829 | `5e6f31c7c90ba34fac2147ef1fec2c18fa6b4f6c796984f6f5a6cd220547c28d` | `bafkreic6n4y4psilunh2yikh54p6ylay7jvu63dzngcpn5ngzurakr6cru` |
| `savante.md` | 7,122 | `2cf2d3b6a42c9438f89c6dc3bae833486e356795a997e8a0f932205d2fe18c3a` | `bafkreibm6lj3njbmsq4prhdnyo5oqm2iny2wpfnjs7ukb6jsebos7ymmhi` |
| `technical.md` | 12,410 | `65e6f9a18ef4c907051a9d416f332f07990a7a695816f683e0316ca2e538413d` | `bafkreidf4342ddxuzedqkgu5ifxtglyhtefhu2kyc33ihybrnsrokocbhu` |
| `todo.md` | 12,293 | `0c5ff3e783a99180e678471222aab60b00982231b712a6ea78433d45a7c54a62` | `bafkreiaml7z6pa5jsgaom6chcirkvnqlacmcemnxcktou6cdhvc2prkkmi` |
| `ui.py` | 53,571 | `de08f5adbac23b855e054052d85b176e8aac1bcf8e4d3786dd2982d90fc61fd0` | `bafkreig6bd223owchocv4bkaklmfwf3orkwbxt4oju3ynxjjqlmq7rq72a` |
| `usage.md` | 4,549 | `8cd688e2d6832d9db4e98cbc23cc9bc5e722c3c09cf71dc083a761f29e431285` | `bafkreiem22eofvudfwo3j2mmxqr4zg6f44rmhqe464o4ba5hmhzj4qysqu` |

## What this proves, and what it does not

- **It proves consistency.** The files, the ledger and the roots agree with each other, and any edit to a
  listed file breaks `sha256sum -c`.
- **It does not prove authorship.** Nothing is signed: anyone with write access can edit a file, re-bind and
  regenerate this proof, and the result will be internally consistent. That is the same limit
  `savante_verify.py` states for the doctrine root.
- **It does not prove time.** The only timestamps are git's and GitHub's. Nothing is anchored on chain, and
  nothing is pinned.
- **It cannot contain its own digest.** `PROOF.md` and `PROOF.sha256` are named by the git blob and commit that
  add them: `git rev-parse HEAD:PROOF.sha256`.
- **What would upgrade it.** A pin whose returned CIDs equal the predicted ones, and then the doctrine root and
  identity written on chain at a mint. Both wait on the operator (`iNFT.md` conditions 2 and 4, `todo.md` §5).
