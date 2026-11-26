# PROOF — Savante, sAGI v0.0.5, generation 10

The digests of the sAGI skill and of every file in this repository that carries a proof: the office, its
bound ledger, the artwork, the verdict records and the tools that check them. Written from the tree of the
commit that adds this file, whose parent is `26da3f6`. Every value here can be recomputed by anyone
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
| doctrine root | `0xd2647b218dbb6b9d09b43fa2a2c02f9ebda325e7166d92c0f9c6b62d9c3a32a0` | is the office still the office? (keccak256 over the persona's 15 doctrine clauses; `0x92fe83eb…ae137d0` from generation 2 to 9, moved in generation 10 by `/embodiment`) |
| bundle root | `0x8d99c0b6e7ad7ad5659483206adf6ffbd112a4ba93f163056ae72d8afb484cbd` | is this the same facet bundle? |
| THOT identity | `bafkreibm2kpdoevzaoifp6n7mcyhf5n2h7bquhg7lvnhrkrmmi7ipy4o4m` | the name of generation 10 (parent `bafkreibxjbzhsyyowcfglwzzm4mbyvdq7wtsqgglplzzl2q4lm56pvwp4m`) |
| identity contentRoot | `0x1115bf789c0cdb1d91c8338f4ac51c968a37c7b90f8bbcc54ecccc08f58e2f55` | the same identity as a keccak256 slot value |
| card | `bafkreidoumbmo7jt5ov7wrfrq6ipbtchgw6umy6nnlj7ppyueeb63blp24` | the public card as written (keccak256 canonical `0xf1e7510d5f008345f7af21f183f4791c26d60f1e8e366fa95f123e3c0d7e941d`) |
| verdict record 1 | `bafkreibke7n3v5ykztl4xpyltf4grhslddpcl3diwavrqpibbh3onqmdhi` | `record_cid`, recomputed from the record with `record_cid` set to null |
| ledger's commit | `4aee1b1fd592c94ce3dc51194dd493fc9da67235` | the commit the ledger hashes (`components_differing_from_head` is `[]`) |

## The artwork

`gfx/Savante3.png`: 154,668 bytes, sha256 `30a59db4ce76dbea8b6a97c143a74996c3c1cd317e3af21f6a18757ae8c5a9a8`, predicted CID `bafkreibquwo3jttw3pviw2uxyfb2osmwypa42ml6hlzb62qyov5orrnjva`. The ledger records it
under `image_candidate.named_by_operator`. The file is JPEG bytes under a `.png` name. Not pinned, so the card's
`image` is null. The other nine images of Savante are in `PROOF.sha256` and indexed in `gfx/README.md`.


## The skill

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `.claude/skills/sagi/SKILL.md` | sAGI skill, v0.0.5 (improve.skill v0.0.38 per .history; the file reads v0.0.1) | 11,907 | `f5147a9bcc978251964121f1e55b0f635ebb5883a97c2108a435f4b4b1612169` | `bafkreihvcr5jxtexqjizmqjb6hsvwd3dl25vra5jpqqqrjbv6s2lcyjbne` |
| `.claude/skills/sagi/.memory` | improve.skill: the raw record (append-only) | 53,260 | `a22b791941d1db3da9dffc5c688d214b2bbbe298dc2fdeef16b3b6a9c9592d77` | `bafkreifcfn4rsqor3m62tx74lrui2iklfo56fgg4f7po6fvtw2u4swjno4` |
| `.claude/skills/sagi/.history` | improve.skill: derived from .memory | 37,269 | `28f4f27fb12233be47571e71a7d98fcae57820a7b1d1e4ffbeade28c09816542` | `bafkreibi6tzh7mjcgo7eovy6ogt5td6k4v4cbj5r2hsp7pvn4kgatalfii` |

## The office: charter, identity and facets (bound in the ledger)

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `.claude/agents/savante.md` | charter (operative) | 7,122 | `2cf2d3b6a42c9438f89c6dc3bae833486e356795a997e8a0f932205d2fe18c3a` | `bafkreibm6lj3njbmsq4prhdnyo5oqm2iny2wpfnjs7ukb6jsebos7ymmhi` |
| `savante.persona` | identity: the .persona | 52,149 | `886dabce06fb5eb3cc061e4ade52b81aa3bb5efc645f0a815f8c0b895f74dc13` | `bafkreieinwv44bx3l2z4ybq6jlpffoa2uo5v57del4ficx4mboev65g4cm` |
| `sAGI.agent` | facet: agent class | 5,461 | `e5a8b0111b3b3d342d5f01057c019044bca46a592ee18ca1ec1e031c4263a650` | `bafkreihfvcybcgz3hu2c2xybav6adecexssguwjo4ggkd3a6amoeey5gka` |
| `sAGI.model` | facet: model (pins none) | 1,636 | `03dbbf5069cfdbcd67747eff1a513217b8139e16e0b4cc74aa71015adb9d3581` | `bafkreiad3o7va2op3pgwo5d674nfcmqxxajz4fxawtghjktrafnnxhjvqe` |
| `sAGI.prompt` | facet: charter body as prompt | 7,191 | `baf5a302bf591b977d45ff21c484cc1279c9693e0f65ae9541db42c042bdcffe` | `bafkreif26wrqfp2zdolx2rp7ehcijtasphewspqpmwxjkqo3ilaefpop7y` |
| `sAGI.tool` | facet: tool allowlist | 3,769 | `ebd3ec9342801ae3dc72840db55e7052b33ff487b6b1fa2e3145e69d9da9ece4` | `bafkreihl2pwjgquadlr5y4uebw2v44cswm77jb5wwh5c4mkf42oz3kpm4q` |
| `sAGI.voaice` | facet: voice | 1,775 | `d4619d4c6fcf0913ed0e2a1616eb219d2bff9a22efbb323a7e579cf44e25862e` | `bafkreigumgouy36pbej62drkcylowim5fp7zuixpxmzdu7sxtt2e4jmgfy` |
| `sAGI.faice` | facet: face | 1,866 | `6e2d33f8e6ad06e56c254549020643ab70b55cb61a6cb0328751ba33b7e3991f` | `bafkreidofuz7rzvna3swyjkfjebamq5loc2vznq2nsydfb2rxiz3py4zd4` |

## The page (canon from generation 10)

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `space/README.md` | page file | 5,691 | `e705449862242fe9bf50e01234af5f532eef405c27dcb9b4656e5c9886f544e1` | `bafkreihhavcjqyref7u36uhaci2k6x2tf3xuaxbh3s43izlolsmin5ke4e` |
| `space/Savante.prompt` | page file | 6,514 | `1ba5b0b5b19b2b58846589ff5021402611b7e3a61d481024ac33e7ccb40494a0` | `bafkreia3uwyllmm3fnmiizmj75iccqbgcg36hjq5jaicjlbt47glibeuua` |
| `space/app.js` | the rooms' wiring (textContent only) | 51,440 | `65c79c04d55e425bd07e1d4c845fa994ec701f02cd27986bf049ca83eed1c753` | `bafkreidfy6oajvk6ijn5a7q5jscf7kmu5ryb6awne6mgx4cjzkb65uohkm` |
| `space/browseml-thread.js` | page file | 1,747 | `8af38a67e81d02ed98f1473426ffd6c97241161d5e2766c578af0b8b906c3b53` | `bafkreiek6ofgp2a5alwzr4khgqtp7vwjojarmhk6e5tmk6fpbofza3b3km` |
| `space/browseml-wasi.js` | page file | 6,575 | `1f91566020e8255c3417086e676af8288a11908902bff027f87994406fb91cca` | `bafkreia7sflgaihievodifyinztwv6biriizbcicx7ycp6dzsrag7oi4zi` |
| `space/browseml-worker.js` | page file | 7,222 | `39cdf331a06e87e31d8406491efc64492e21da48f83ca367ece4ddabfd56feb8` | `bafkreibzzxztdidoq7rr3bagjeppyzcjfyq5ushyhsrwp3he3wv72vx6xa` |
| `space/browseml.js` | page file | 7,233 | `90bf5d44b1f40ea93960d0fae514cfdd94f00a764288f9052be2615623059d4a` | `bafkreieqx5oujmpub2utsygq7lsrjt65styau5scrd4qkk7cmflcgbm5ji` |
| `space/cluster.js` | page file | 18,937 | `ebf034ca1c259e55c2e1d2dad2158542ebdf0bd33325bfa7d9e313ca134b52b8` | `bafkreihl6a2muhbftzk4fyos3ljblbkc5ppqxuztew72pwpdcpfbgs2sxa` |
| `space/faicey.css` | Faicey: the split face | 6,708 | `da3e239d94dff70a8d20ea209140a46463e609e29554d95642ad6467597d068b` | `bafkreig2hyrz3fg764fi2ihkeciubjdemptatyuvktmvmqvnmrtvs7igrm` |
| `space/faicey.js` | Faicey: voaicey, oscilloscope mouth, camera eye, microphone ear | 17,674 | `61fd45e981add116530bfa4a5bb8bda43f8683d0c1cdc14131465fdd1985f58a` | `bafkreidb7vc6tann2elfgc72jjn3rpneh6dihugbzxaucmkgl7ortbpvri` |
| `space/history.json` | page file | 2,931 | `1cc8f9bb85e469bdb250c0ef205d88b34f1aeb2430e6f51f125055ba1275aa60` | `bafkreia4zd43xbpeng63euga54qf3cftj4nowjbq432r6esqkw5be5nkma` |
| `space/index.html` | the page: rooms and markup | 28,787 | `4a35fae37d4462207842323d199e607772556277a86710b13ca4cd084c02821a` | `bafkreickgx5og7kemiqhqqrshumz4ydxojkwe55im4ilcpfezueeyaucdi` |
| `space/interactive/README.md` | page file | 7,380 | `64420dc910fdba5cf94f5fe304a32f1f93d477e52a231240e526dbebf68cd0ba` | `bafkreideiig4seh5xjopst274mckgly7spkhpzjkemjebzjg3pv7ndgqxi` |
| `space/interactive/app.js` | page file | 61,528 | `fb3f4f8aba4c36c73f622011cae7756b080cc2da734534f70e3b12a052e258d4` | `bafkreih3h5hyvosmg3dt6yrachfoo5llbagmfwttiu2podr3ckqffysy2q` |
| `space/interactive/index.html` | page file | 28,066 | `caf9fd92cc7ef271913d7a0c08106e24fac12f17c4cb6e29a93461353a2f9b87` | `bafkreigk7h6zftd66jyzcpl2bqeba3re7las6f6eznxctkjume2tul43q4` |
| `space/interactive/style.css` | page file | 15,905 | `fc869342b97104b1ba084989fa844ee13ab72ce7fee624e4d33338c8a773eb02` | `bafkreih4q2jufolrasy3uccjrh5iitxbhk3szz764ysojuzthdeko47lai` |
| `space/pythai.js` | page file | 3,990 | `dbee2f1d556837bb5f12c8fb432a576f75fb67500cc90b40c420c6341f23f017` | `bafkreig35yxr2vlig65v6ewi7nbsuv3pox5wouamzefubrbayy2b6i7qc4` |
| `space/savante.js` | pure functions: integrity, verdict, Hub and PYTHAI readings | 14,104 | `db1a7e5e39f0863510f7ba84b36bc136af66e4d1726b5dfb159fb25adc182caf` | `bafkreig3dj7f4opqqy2rb552qszwxqjwv5tojulsnno7wfm7wjnnygbmv4` |
| `space/savanteml.js` | page file | 4,745 | `9295c99a6f5da831fcfb20edd7a6c004e37b775b60d359ca7251ca4751b3a1b2` | `bafkreiessxezu325vay7z6za5xl2nqae4n5xow3a2nm4u4srzjdvdm5bwi` |
| `space/serve.py` | lays the Space out and serves it locally | 6,866 | `597967c144d2c35f007b03ecd2813ecf0090cde5f3444de42285c028b5532f87` | `bafkreiczpft4crgsynpqa6yd5tjicpwpacim3zptirg6iiufyaulkuzpq4` |
| `space/skills/huggingface/SKILL.md` | page file | 4,337 | `6bd22d8973b3933c603466b8b75ff1fe6d873188d710a048028d3c332b7f1da4` | `bafkreidl2iwys45tsm6gandgxc3v74p6nwdtdcgxccqeqaunhqzsw7y5uq` |
| `space/style.css` | page file | 14,365 | `73d1e7fa799cd425b2dab6b6eb16cc063a8dedd2b2b9e8e24e7a53185b7c1c03` | `bafkreidt2ht7u6m42qs3fwvww3vrntaghkg63uvsxhuoett2kmmfw7a4am` |
| `space/uiftabs.js` | page file | 5,525 | `8a1ffc914d1868a578e722056c5410f414103a1fb0d1e3d667f2b66bdfeec44b` | `bafkreiekd76jctiyncsxrzzcavwfiehucqiduh5q2hr5mz7swzv573wejm` |
| `space/views/skill-landing.txt` | page file | 725 | `86b4b2650eaa06f11838bc83a1f6bb87a7fdde22edfb666eea13f4797636aca6` | `bafkreiegwszgkdvka3yrqof4qoq7no4hu7654ixn7ntg52qt6r4xmnvmuy` |
| `space/views/skill-marketing.txt` | page file | 975 | `4335983244ddda413bf0671cb7d46b95be19412520f5f5e8676b44f11202b731` | `bafkreicdgwmderg53jatx4dhds35i24vxymucjja6x26qz3lityreavxge` |
| `space/views/skill-public.txt` | page file | 2,031 | `1a1cbfa4a8225e1e6c4e623005fb057566913f5e1f1ba80fbd59be376903b096` | `bafkreia2ds72jkbclypgyttcgac7wblvm2it6xq7doua7pkzxy3wsa5qsy` |

## Derived by the binder (never hand-edited)

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `savante.agentcard.json` | public card: EIP-721 metadata + ERC-8004 registration | 8,024 | `6ea302c77d33ebabfb44b18790f0cc4735bd4663cd6ad3f7bf142103ed856fd7` | `bafkreidoumbmo7jt5ov7wrfrq6ipbtchgw6umy6nnlj7ppyueeb63blp24` |
| `savante.commitments.json` | integrity ledger | 17,500 | `bede5c8e628e10f62f600af6988d2afd50b0ca3204eb293a41c0dba89f818ea1` | `bafkreif63zoi4yuocd3c6yak62mi2kx5kcymumqe5mutuqoa3ouj7amoue` |
| `savante.thot.json` | THOT manifest, generation 10 | 9,032 | `c30362e8701d95c9c0b23b74801319f1c79eabc0ca45a4da5d7f679a5e973746` | `bafkreigdanroq4a5sxe4bmr3osabggpry6pkxqgkiwsnuxl7m6nf5fzxiy` |

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
| `ci/gate-runs/0004/verdict.md` | CI gate run 0004 (generation 8) | 6,885 | `cd7e21698b51560d108e94679aba86cf1f2b427778c806ccbd779d36f3b0ff96` | `bafkreignpyqwtc2rkygrbduum6nlvbwpd4vue53yzadmzplxtu3phmh7sy` |
| `ci/gate-runs/0005/verdict.md` | CI gate run 0005 (generation 10) | 4,553 | `363fb7fb2df122f599a8a7f7fbaab59d0f8cf421a7fa8a431404e3274f56623a` | `bafkreibwh637wlprel2ztkfh6752vnm5b6gpiinh7kfegfae4mtu6vtchi` |
| `ci/gate-runs/0002/verdict.md` | CI gate run 0002 | 8,564 | `15abbccf1fff83aa76b76ebc16566a2188c1d972f43d5ab3868896a613dc8e29` | `bafkreiavvo6m6h77qovhnn3oxqlfm2rbrda5s4xuhvnlhbuis2tbhxeofe` |

## The tools that make and check the proofs

| file | what | bytes | sha256 | CID (predicted) |
|---|---|---:|---|---|
| `bind/savante_bind.py` | binder (operator's tool) | 93,653 | `0959a91decaf3a12bdf38231a15a7587d8b5f0711f1a8dcb3c01b09843896c1d` | `bafkreiajlgur33fphijl344cggqvu5mh3c27a4i7dkg4wpabwcmehclmdu` |
| `bind/savante_verify.py` | verifier (anyone's tool) | 63,480 | `fe7cdfb7bef42d43fed97df00b103575ae3779a094631201a34ebf5bcf9ae31b` | `bafkreih6ptp3ppxufvb75wl56afranlvvy3xtieummjadi2ox5n47gxddm` |
| `bind/skill_history.py` | .memory → .history projection and checks | 7,677 | `3ba21760b395f815a24af537cbeba72e1c358c15cced0c37b1e7b2ddf7cbcfb9` | `bafkreib3uilwbm4v7ak2esxvg7f6xjzodq2yyfom5ugdpmphwlo7ps6pxe` |

## Everything else

| file | bytes | sha256 | CID (predicted) |
|---|---:|---|---|
| `.gitignore` | 19 | `862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793` | `bafkreiegejr7uh2gyihq2hsnvrp7zr22xvk4baqrwlbymtc7q5sltwdxsm` |
| `LICENSE` | 1,091 | `3970382bf4f5fc6adaaff98835fbfd8a01bb1d3ec249b8ab07395e06b1363e3c` | `bafkreibzoa4cx5hv7rvnvl7zra27x7mkag5r2pwcjg4kwbzzlydlcnr6hq` |
| `MANIFESTO.md` | 7,186 | `4023714ef1226b0d8a646b3bfcd9d351db3310965101c71b43cf3ff18dce5726` | `bafkreicaenyu54jcnmgyuzdlhp6ntu2r3mzrbfsrahdrwq6ph7yy3tsxey` |
| `README.md` | 21,780 | `cf044c69c7ef6f8d3284502ffd392b7d27383756e44e908c6ace8f94034e0188` | `bafkreigparggtr7pn6gtfbcqf76tsk35e44dovxej2iiy2wor6kagtqbra` |
| `SAVANTE_AS_A_SERVICE.md` | 5,341 | `e401f81b895bcb67341610460f792689c8b90fbbde16dc52e0091e38eb8e4952` | `bafkreiheah4bxck3znttifqqiyhxsjujzc4q7o66c3offyajdy4oxdsjki` |
| `Savante.md` | 7,427 | `7a29ebc05085e23ff75a9144e22690b27988f3ac3fbeeddce5678b21ea2361ab` | `bafkreid2fhv4auef4i77owuritrcnefspgephlb7x3w5zzlhrmq6ui3bvm` |
| `bind/savante_publish.py` | 11,180 | `fe0162d26e416edb1ff068cf37ad905d466f1b78287538389095347574d08315` | `bafkreih6afrne3sbn3nr74diz4323ec5izxrw6biou4dreevgr2xjuedcu` |
| `ci/gate-runs/0001/meta.txt` | 1,665 | `3fdb410b95aaceb04a07143313cdddb00e4a052c82e65b26cb7991fe94ecaba7` | `bafkreib73naqxfnkz2yeubyugmj43xnqbzfaklec4znsns3zsh7jj3flu4` |
| `ci/gate-runs/0002/meta.txt` | 775 | `745c71d6b0bbdb02c5fbf5e3a0127b25438e96e86cbec67063e3ba98ef269973` | `bafkreidulry5nmf33mbml67v4oqbe6zfiohjn2dmx3dhay7dxkmo6juzom` |
| `ci/gate-runs/0003/meta.txt` | 950 | `c8d726b6501199a5a439cad3d5b9c8d6c89858cf88680773be9cf9dc32e4d178` | `bafkreigi24tlmuartgs2iook2pk3tsgwzcmfrt4inadxhpu47hodfzgrpa` |
| `ci/gate-runs/0004/meta.txt` | 1,678 | `90b65f31e8754fd660de0858439f5c61e8d62d5052340580079c07df62683a1b` | `bafkreieqwzptd2dvj7lgbxqilbbz6xdb5dlc2ucsgqcyab44a7pwe2b2dm` |
| `ci/gate-runs/0005/meta.txt` | 1,748 | `bdf3fa53b94961d2163ab1b39969328de7286918dc796d1dcdd00e12a2d4e7e3` | `bafkreif56p5fhokjmhjbmovrwomwsmun44ugsgg4pfwr3toqbyjkfvhh4m` |
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
| `iNFT.md` | 43,531 | `a0fd3fbe2ae77b9a9aca19d05d5029987426a7d3f7e4213067f925f4f158c7d4` | `bafkreifa7u734kxhponjvsqz2bovakmyoqtkpu7x4qqtaz7zex2pcwgh2q` |
| `llm.txt` | 16,249 | `3820dd640ae92e8521f11a0b293849ded5bb475d44863bf8423f7fa2093cdfb4` | `bafkreibyedowicxjf2csd4i2bmutqso62w5uoxkeqy57qqr7p6raspg7wq` |
| `sAGI.md` | 6,829 | `5e6f31c7c90ba34fac2147ef1fec2c18fa6b4f6c796984f6f5a6cd220547c28d` | `bafkreic6n4y4psilunh2yikh54p6ylay7jvu63dzngcpn5ngzurakr6cru` |
| `savante.md` | 7,122 | `2cf2d3b6a42c9438f89c6dc3bae833486e356795a997e8a0f932205d2fe18c3a` | `bafkreibm6lj3njbmsq4prhdnyo5oqm2iny2wpfnjs7ukb6jsebos7ymmhi` |
| `technical.md` | 12,498 | `fb2e2d12637bbd947dae05255b228331e0b630580a9b20da939be1304888b3c8` | `bafkreih3fywrey33xwkh3lqfevnsfazr4c3dawaktmqnve434eyercftza` |
| `todo.md` | 23,981 | `f3b81373be38f0e5bdbe902dd1f39883b88b47c4a8fe2f367cc9374ff7307482` | `bafkreihtxajxhpry6ds33puqfxi7hgedxcfuprfi7yxtm7gjg5h7omduqi` |
| `ui.py` | 63,909 | `926e7b8e90f5395eb24ce6e52e6d13c42135e268b95f3fce7ee184f8a8aef6fd` | `bafkreiesnz5y5ehvhfplethg4uxg2e6eee26e2fzl47447xbqt4krlxw7u` |
| `usage.md` | 5,106 | `4337a13d09671f9793e9efb1b1591cc8870a62c93eef67faab618ab01850c7d6` | `bafkreicdg6qt2clhd6lzh2ppwgyvshgiq4fgfsj655t7vk3brkybqugh2y` |

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
