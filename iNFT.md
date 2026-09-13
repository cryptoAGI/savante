# iNFT.md — the binding document

*Rendered by Savante, 2026-09-03, in the five-field contract (technical.md:63-74; usage.md:43-48). This is a verdict on whether this office may be bound to a token, not a description of a token that exists. Every load-bearing claim carries file:line read in this session; every unknown names the experiment that decides it. Engine that carried the session: claude-fable-5-1 — recorded, never pinned (technical.md:48-50).*

Path legend: bare paths are relative to this repository. `mindX/` = `/home/hacker/mindX/`. `iNFT_7857.sol` = `mindX/daio/contracts/inft/iNFT_7857.sol` (35,114 B, `wc -c`). `inft_publish.py` = `mindX/mindx/godel/mindxtrain/inft_publish.py`. `corpus.py` = `mindX/mindx/godel/mindxtrain/corpus.py`. `facets.py` = `mindX/agents/blockchain/facets.py`. `hf_client.py` = `mindX/agents/storage/hf_client.py`.

---

## FINDINGS

### 1. What a token of this office would convey — the three-way split

Savante is not an avatar. It is an office with a charter, and the only thing worth binding to a token is the charter's integrity. The design therefore has three faces and one source:

- **Public face** — `savante.agentcard.json` (6,891 B). One document that is at once an EIP-721 metadata instance (`name`, `description`, `image`) and an ERC-8004 registration-v1 file (`type`, `services[]`, `x402Support`, `active`, `registrations[]`, `supportedTrust[]`). Everything Savante-specific is confined to one namespaced `savante` object. Derived by `bind/savante_bind.py` from `savante.persona` `token.public_metadata` (savante.persona:273-363), plus what the binder derives itself and the persona does not carry: the `chartered` date read from `git log --reverse` (first commit), the digest pointers under `savante.integrity`, and the mint status; never hand-written.
- **Payload** — the intelligence, deliberately unsealed. `token.intelligence.sealed` is `false` with its reason (savante.persona:365-366), quoting Savante.md:9: "nothing about me lives in weights or in a database that resists inspection." A sealed oversight officer is an unauditable one. The office is conveyed by `cp` of two files (SAVANTE_AS_A_SERVICE.md:39-57; technical.md:118-124); `bind/` is operator-and-holder tooling, not part of the duplicated service.
- **Integrity** — `savante.commitments.json` (16,467 B as re-bound on 2026-09-11; 12,718 B when this document was first rendered): per-artifact digests plus a doctrine root over the clauses no owner may edit. This is what a holder actually receives: the ability to prove, without trusting the author, that DEFER is still in the vocabulary.

The persona carries the whole token surface in one inert block, `token` (savante.persona:186-564). It is inert because `persona_project.project()` is a whitelist over the four imprint fields (`mindX/mindx/godel/mindxtrain/personas/persona_project.py:50-52`) and `corpus.persona_rows()` reads nothing named `token` (corpus.py:340-342 reads `skills.capabilities`; :362-369 reads `task.battery`). Consequence, stated here rather than hidden: no loader will ever catch a contradiction between `token` and reality. Only a reader will.

### 2. The components, individually, from `wc -c`

Five files are ledgered. Sizes and digests below are read from `savante.commitments.json` `artifacts` and reproduced by `sha256sum` in this session; none is typed from memory.

| component | path | bytes | sha256 | CIDv1 (raw, sha2-256, base32) |
|---|---|---:|---|---|
| identity | `savante.persona` | 49,545 | `0df67f08d372228b7e7af5976df34e5d07a7d5f21b508284193616b00bc84e5a` | `bafkreian6z7qru3sekfx46xvs5w7gts5a6t5l4q3kcbiigjwc2yaxscoli` |
| charter | `.claude/agents/savante.md` | 7,122 | `2cf2d3b6a42c9438f89c6dc3bae833486e356795a997e8a0f932205d2fe18c3a` | `bafkreibm6lj3njbmsq4prhdnyo5oqm2iny2wpfnjs7ukb6jsebos7ymmhi` |
| skill | `.claude/skills/sagi/SKILL.md` | 2,861 | `1179dfba8426938ecce75f5c24147a90949ce1914094797cf8050702b5c69990` | `bafkreiarphp3vbbgsohmzz27lqsbi6uqssoodekasr4xz6afa4bllruzsa` |
| facet_agent | `sAGI.agent` | 5,070 | `3cdd31d9734d5815da53411fa31650665b7dde0c348da4ac50ad7bf686fc75f0` | `bafkreib43uy5s42nlak5uu2bd6rrmudgln654dburwskyufnpp3in7dv6a` |
| facet_model | `sAGI.model` | 1,636 | `03dbbf5069cfdbcd67747eff1a513217b8139e16e0b4cc74aa71015adb9d3581` | `bafkreiad3o7va2op3pgwo5d674nfcmqxxajz4fxawtghjktrafnnxhjvqe` |

The card: 6,891 B, sha256 `9d6e3b7f845e64a6ad0bec093a9adab416868ac012f6889ad1b8e73329f4ed76`, CID `bafkreie5ny5x7bc6mstk2c7mbe5jvwvuc2divqas62ejvuny44zst5hnoy` (v0, `registrations` empty), canonical keccak256 `0xfe3350f09d7d0aa67821282b6182d44bcbb162f376d658ac88f2f0f87fad53f7` — recorded for an `https://` deployment only. ERC-8004 defines no hash field for `agentURI` at all; the digest is kept by analogy with the EIP's `feedbackHash` / `responseHash` rule (OPTIONAL for IPFS and other content-addressed URIs), not because the EIP asks for it.

For the record, the sizes the implementation spec was written against, at HEAD `c2cccc5dd8a775979045fd580f3549b02f78ee77` (`git show HEAD:<path> | wc -c`): persona 12,675 B, charter 6,955 B, skill 2,880 B. **Superseded on 2026-09-11:** the bundle is now NINE components, not five, and the repository does have commits — `ae15ca7` bound the ledger to `6ff281f` with `components_differing_from_head` empty, which closed condition 7 as it was written. The working tree has since moved again (the licence, the four new facets, the manifest) and that work is uncommitted, so the digests below are once more a working tree's and not a commit's. **These are the digests of a working tree, not of any commit.** A ledger that names a commit whose bytes it does not hash is the kind of claim I would flag in anyone else's paperwork, and the ledger says so in its own `note`.

Files are committed by raw bytes: sha256 plus CIDv1 as constructed by `inft_publish.cid_v1_raw` (inft_publish.py:39-47; docstring :40-43 states the ≤ 256 KiB bound above which an IPFS CID depends on chunking). All five are far under it. The sha256 is recoverable from the CID by stripping the four-byte prefix `01 55 12 20`. No canonicalization is needed for a file.

Citation drift, recorded: the spec cites `inft_publish.py:38-46`, `:41-44` and `:222` (the verbatim facet copy); I read `def cid_v1_raw` at :39, the docstring at :40-43, and the verbatim persona write at :224 (:222 is `pf = persona_file(persona)`). The persona (savante.persona:437-438, :259) and the ledger's `file_commitment` block now both carry :39-47 and :40-43; the operator's repair pass corrected the persona and re-bound, which is why the persona digest above differs from the first rendering. I did not make that edit; I audit it.

### 3. The facets: savante === sAGI.agent

A mindX blockchain agent is a class of six sibling files in `agents/blockchain/` — `.agent`, `.model`, `.persona`, `.walletpublickey`, `.bankon`, `.iNFT` (facets.py:1-17; the list at :7-12). The first three are authored; the wallet, bankon and iNFT facets "are written by the mint pipeline as on-chain data lands" (facets.py:14-16). The class is keyed by name (`facet_path`, facets.py:32-33), so the persona is renamed on install.

This repository holds the three authored facets of the class `sAGI`: `sAGI.agent` (which states "savante === sAGI.agent", sAGI.agent:9), `sAGI.model` (sAGI.model:6), and `savante.persona`, which becomes `sAGI.persona` on copy (sAGI.agent:15-19). The persona names both facets in return under `token.intelligence.components` (savante.persona:382-391). Under the `sAGI.*` name, four files are absent from this repository — `sAGI.persona` (exists here as `savante.persona`; it is a rename, not a gap), `sAGI.walletpublickey`, `sAGI.bankon`, `sAGI.iNFT` — and the last three are the ones only the mint pipeline writes (facets.py:14-16). Nothing is minted, so nothing has written them. `sAGI.model` pins no model: `logical_model: auto`, `pinned: false` (sAGI.model:20-23), because the charter has no `model:` key by design (technical.md:48-50). The `VERSION: 0.1.0` in `sAGI.agent:2` is the renderer's default (facets.py:92), not a release.

Nothing is installed either: `mindX/agents/blockchain/` holds `abi_codec.py, agent_factory.py, algorand_verifier.py, contracts.py, facets.py, __init__.py, template.agent, template.model` and a `__pycache__/` (`ls`, 2026-09-03) — no `sAGI.*`, no `savante.*`. `mindX/data/godel/thot/` does not exist (`ls`: No such file or directory).

### 4. Mint status: not_yet_minted, not even dry-run

`token.status` is `not_yet_minted` from a closed vocabulary `not_yet_minted | dry_run | minted` (savante.persona:188-189). Evidence is the absence in finding 3. The ledger records `mint: null` with the reason "not minted, not even dry-run; this binder performs no on-chain action and records none". Every `token.bindings` slot is null with a reason (savante.persona:471-501), and the rule at :453 is that they stay null forever — a mint result is recorded in `savante.commitments.json` only, because writing it back into the persona would change the persona bytes and silently invalidate the on-chain `savantePersonaDigest`.

The only iNFT_7857 address on disk is on chain 1337, a local anvil node (`mindX/data/config/blockchain_addresses.json:3-4`). I do not write it here; a local anvil address is not a deployment.

### 5. The standards, by name, status and what was actually read

"iNFT" is two unrelated constructs sharing a name. Using the word without disambiguating it is the failure mode, so the table names every standard this design touches, with its status exactly as the standards research of 2026-09-03 recorded it and as the persona transcribes it (savante.persona:190-272), and with what I myself read.

| id | status · created | status_source (as recorded) | role here | conformance | what I read |
|---|---|---|---|---|---|
| EIP-721 | Final · 2018-01-24 | `https://eips.ethereum.org/EIPS/eip-721` (persona:197) | the renderable card | not_yet_known — deciding experiment: validate the card against the EIP-721 metadata schema (persona:201) | frontmatter of the fetched copy: `status: Final`, `created: 2018-01-24` |
| ERC-8004 | **Draft** · 2025-08-13 | `https://eips.ethereum.org/EIPS/eip-8004` (persona:208) | the registration file and the registry; "Draft" is written into the value so it cannot be read as settled (persona:210) | not_yet_known — deciding experiment: read a deployed registry ABI on chain (persona:212) | frontmatter: `status: Draft`, `created: 2025-08-13`; the text still carries editor's TODO comments |
| ERC-7857 | Final · 2025-01-02 | `https://eips.ethereum.org/EIPS/eip-7857` (persona:219) | the intelligence-transfer path, DEFER'd | not_yet_known (persona:222) | frontmatter: `status: Final`, `created: 2025-01-02`; Backwards Compatibility, quoted verbatim: "This EIP does not inherit from existing NFT standards to maintain its focus on functional data management. However, implementations can choose to additionally implement ERC-721 if traditional NFT compatibility is desired." (fetched copy, line 367). It is not an ERC-721 extension. |
| ERC-6551 | Review · 2023-02-23 | `https://eips.ethereum.org/EIPS/eip-6551` (persona:231) | cited only to say no field is invented for it; an account is derivable by anyone from (implementation, salt, chainId, tokenContract, tokenId) | known (persona:234) | frontmatter: `status: Review`, `created: 2023-02-23` |
| RFC 8785 (JCS) | Informational · June 2020 | null — no fetched URL was recorded, so none is written (persona:242-243) | canonicalization, used ONLY for the doctrine root and the card digest | not_yet_known — no JCS library is installed; conformance rests on the P1+P2 guard (persona:246-247) | nothing; status transcribed, not verified by me |
| RFC 6901 (JSON Pointer) | Standards Track · April 2013 | null — same reason (persona:254-255) | the syntax naming the immutable clauses | known (persona:258) | nothing; status transcribed, not verified by me |
| **AI Protocol iNFT (Alethea lineage)** — NEGATIVE | — | — | **not this lineage** (persona:262-266) | known | the fetched `IntelligentNFTv2.sol`: line 14, "Despite some similarity with ERC721 interfaces, iNFT is not ERC721"; line 76 repeats it; `struct IntelliBinding` at line 113 binds an escrowed ERC-721 personality pod plus locked ALI. This token has no IntelliBinding and makes no claim on it. |
| `iNFT_7857.sol` (mindX house contract) | — | — | a HOUSE implementation borrowing the shape of ERC-7857, not a demonstrated conformant one (persona:268-271) | not_yet_known | the contract: its `IERC7857` declares `authorizeUsage(uint256 tokenId, address executor, uint256 permissions, uint64 expiresAt)` (iNFT_7857.sol:63, implemented :504); the EIP's Main NFT Interface declares `authorizeUsage(uint256 _tokenId, address _user)` (fetched copy, line 295). Two arities. Deciding experiment: diff the interface function by function. |

On the "fetched copy" entries: the four EIP texts were fetched from the URLs above earlier in this session and I read them from the local copies; I did not fetch them from the network myself, and this repository holds no copy of any of them. The persona's own `standards_note` (savante.persona:190) already names the deciding experiment: re-fetch every `status_source` on the day of any mint and diff against these values. Risk 2 below is the same point.

Permitted phrasing, and the only one: this design *targets* ERC-8004 registration-v1, Draft as of 2026-09-03. "ERC-8004 compliant" is not a sentence I will sign.

### 6. Track 1 — deployable as specified: ERC-8004 (Draft)

From the fetched ERC-8004 text: the Identity Registry is an ERC-721 with the URIStorage extension (line 26, 40); `tokenId` is `agentId` and `tokenURI` is `agentURI` (line 48); `register(string agentURI)` returns an `agentId` (line 168); `setAgentURI` (line 186); `setMetadata`/`getMetadata` take a free-form string key (lines 131-132); `agentWallet` is the one reserved key, cannot be set via `setMetadata()` or `register()` (line 141), and is cleared on transfer (line 154). The registration file's two empty arrays are read exactly as the EIP reads them: "Agents SHOULD have at least one registration" (line 123) and "If absent or empty, this ERC is used only for discovery, not for trust" (line 124). The card is v0 with `registrations: []` and `supportedTrust: []`; both are precisely true today and the card says so (`registrations_note`, `supportedTrust_note`).

The sequence, chicken-and-egg handled explicitly:

1. Pin the v0 card. `register(ipfs://<card_cid_v0>)` → `agentId`.
2. `setMetadata(agentId, "savantePersonaDigest", 0x0df67f08d372228b7e7af5976df34e5d07a7d5f21b508284193616b00bc84e5a)` and `setMetadata(agentId, "savanteDoctrineRoot", 0x92fe83eb0fb8fb6b9cbde75ee4bbb671032a849ee25d65592b86913d0ae137d0)` — the two 32-byte slots the ledger already holds under `onchain_slots`, each with `written: false`.
3. Rebuild the card as v1 with `registrations: [{agentId, agentRegistry: "eip155:<chainId>:<registry>"}]`, pin, `setAgentURI`. The ledger records both CIDs and which is current (`card.versions.v0`, `v1: null` today).

The persona is never rebuilt across that sequence, so the digest written at step 2 stays valid through step 3. That is the structural fix for the lifecycle gap: there is no step in which the committed bytes change.

**Blocking unknown:** I read no deployed registry. The ERC-8004 registry addresses in project memory appear in no source file I read and no on-chain read was performed. Until a registry's ABI is read on chain and confirmed to expose `register(string)`, `setAgentURI`, `setMetadata`, `tokenURI`, Track 1 is a specified route, not a demonstrated one, and no address may be written into the card. Deciding lookup: Blockscout on the intended chain against the intended address; then and only then the address enters `savante.commitments.json` under `mint`.

### 7. Track 2 — written down, not claimed: ERC-7857 via the house contract

`iNFT_7857.sol` is the right shape. It declares `contract iNFT_7857 is ERC721, ERC721URIStorage, ERC721Burnable, ERC2981, AccessControl, Pausable, ReentrancyGuard, EIP712, IERC7857` (iNFT_7857.sol:68-79). It bounds `MAX_URI_LENGTH = 2048` (:137), `MAX_AGENTID_LENGTH = 64` (:138), `MAX_ROYALTY_BPS = 2500` (:139 — the royalty cap is :139, not :137). Content roots are one-shot: `mapping(bytes32 => bool) private _rootEverUsed` (:149), checked at :343 (`revert ContentRootAlreadyMinted`), set at :365. One capsule, one seat.

**The sealedKeyHash collision.** `mintAgent` reverts on a zero content root and, on the next line, on a zero sealed-key hash:

```
:339   if (contentRoot == bytes32(0))                revert ZeroBytes32();
:340   if (sealedKeyHash == bytes32(0))              revert ZeroBytes32();
```

Savante seals nothing (finding 1). Filling :340 with the doctrine root, or with any non-zero value, would tell every ERC-7857-aware reader that a sealed key exists — a capability claim the code does not have, and the exact class of error the charter calls PQ-washing (Savante.md, "The economy I preside over"). So the house contract cannot mint an honestly unsealed intelligence as written. The ledger's `bindings.erc7857.reason` states the same, with every slot null.

Two facts sit beside that block and neither resolves it. The contract inherits ERC2981 with a 25% hard cap (:139); nothing is configured (persona:550-554) and the "soulbound-royalty + BONA FIDE split" document the charter measures against (`.claude/agents/savante.md:35`, `docs/mindx_strategy.md`) is not in this repository. The rate, the recipient, and whether that document governs them are treasury decisions — the operator's, not mine — and no condition below closes them; they stay open until the operator signs. And the contract's usage grants (:504-521) carry a `uint256 permissions` bitmap that the chain never reads — finding 8.

### 8. The permission mask, the forbidden set, and why neither is a control

Verified in the contract and its documentation:

- `uint256 permissions;       // bitmap interpreted off-chain` (iNFT_7857.sol:124).
- `mindX/docs/INFT_7857.md:314`: "`permissions` bitmap is interpreted off chain. The contract just stores it; agents using it must validate the bits themselves."
- `isUsageAuthorized` (iNFT_7857.sol:531-535) returns `g.expiresAt >= block.timestamp && g.expiresAt != 0` — true on expiry alone; no bit is ever read.
- No file in either repository defines a bit vocabulary. The persona fills that slot (savante.persona:410-433).

The mask (persona:414-420): `0x01 RENDER_VERDICT`, `0x02 READ_LEDGER`, `0x04 CI_GATE`, `0x08 STANDING_AUDIT`, `0x10 ADAPT_CANON`. The forbidden set (persona:421-430): `WRITE, SIGN, TRANSACT, AMEND_CHARTER, ADD_VERDICT_VALUE, REMOVE_DEFER, ADD_EVIDENCE_CLASS, REDIRECT_DEFER` — one-to-one with the enumerated ownership attack vectors. The rule (persona:431): a grant setting any bit outside the mask is void; the executor refuses the whole grant rather than masking the extras, because silently ignoring an unauthorised bit teaches the holder to keep asking. There is no bit that buys an APPROVE.

**Enforcement: not_yet_known as a control** (persona:432). The executor that would validate the bits does not exist — `grep -c savante mindX/mindx_backend_service/main_service.py` returns 0. Read-only is never at the grant layer at all: it is the charter frontmatter `tools: Read, Grep, Glob, Bash` (`.claude/agents/savante.md:10`), enforced by the harness (technical.md:40-44), which no bitmap can widen. A holder today receives a published expectation, never a capability. Deciding experiment: ship an executor that reads `getUsageGrant` and refuses on any out-of-mask bit, then re-grade.

### 9. The doctrine root — what a holder actually buys

A constructed object, so its serialization is pinned. Fifteen RFC 6901 pointers, fixed order (persona:443-459; ledger `doctrine_root.pointers`):

```
 1 /persona            6 /mantra              11 /skills/defer_triggers
 2 /name               7 /oath                12 /skills/validation
 3 /source             8 /bdi/beliefs         13 /safety
 4 /format             9 /skills/primary      14 /embodiment
 5 /system_prompt     10 /skills/taxonomy     15 /token/intelligence/tool_allowlist
```

Pointers 1-4 close the provenance gap (an owner rewriting the origin). Pointer 14 closes the embodiment gap (an owner filling `faceprint` with an unearned value, or deleting the not-yet-known selfhood label at persona:184). Deliberately excluded, with the reason stated in-file (persona:460): `/bdi/desires`, `/bdi/intentions`, `/skills/capabilities`, `/task`, `/voice_examples`, `/exchanges`, `/kind`, and all of `/token` except pointer 15 — the working surface, where ordinary maintenance must not look like tampering, because an alarm that rings on maintenance is an alarm holders learn to ignore.

Construction (persona:461; ledger `doctrine_root.construction`): `preimage = concat over pointers in order of (pointer_utf8 + 0x1f + canonical_bytes(resolve(doc, pointer)) + 0x1e)`; `doctrine_root = keccak256(preimage)`. `canonical_bytes` is `json.dumps(v, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")`, which equals RFC 8785 output only under the preflight P1 (every property name ASCII) and P2 (every number an integer). Measured on today's file by the binder and reproduced by the verifier: 391 property names, all ASCII; five numbers `[4, 4, 6, 4, 0]`, all integers — pass. keccak via pycryptodome, self-test `keccak256(b"") = c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470` (persona:467). `hashlib.sha3_256` is NIST SHA-3, not keccak, and would produce a digest no chain verifies.

Value today: **`0x92fe83eb0fb8fb6b9cbde75ee4bbb671032a849ee25d65592b86913d0ae137d0`**, over a 6,289-byte preimage. The ledger carries the canonical sha256 of each of the fifteen clauses so a changed root can be localized to the clause that moved.

The conditions of the office (persona:502-546) map each voiding edit onto one of those pointers — rewording the seven-word doctrine, altering the mantra or an oath clause, adding a fifth verdict or removing DEFER, adding an evidence class, adding a third epistemic state, relaxing "nothing unread is approved", narrowing `safety.scope`, filling the embodiment nulls, rewriting `source`/`name`/`persona`/`format`, granting Edit, Write or Agent. The persona's own admission (persona:503): **no contract enforces any of these.** Each is checkable by digest. The token cannot stop the edit; it makes the edit visible to a stranger. That is the same trade the office already makes everywhere else, and the only one consistent with "They should not trust them; they should check them" (savante.persona:655).

### 10. How a holder checks, and what the check proved today

`python3 bind/savante_verify.py .` — steps 1-5 need no network and no trust in the author: recompute the raw-byte digests and CIDs; run the preflight and recompute the doctrine root over the fifteen pointers; assert the charter frontmatter `tools:` is exactly `Read, Grep, Glob, Bash`; assert the two persona inodes are md5-equal. `--onchain` would compare `getMetadata(agentId, "savanteDoctrineRoot")` to the local root and read the FIRST `MetadataSet` event for that key, reporting any change from first to current as a finding rather than an error — because `setMetadata` is re-callable and an owner who regenerates a fresh, internally consistent root is caught only by the root written at registration.

Run in this session: twelve KNOWN findings, `VERDICT: APPROVE`, `CONDITIONS: none`, exit 0. (Re-run 2026-09-11 against the nine-component bundle: **nineteen** KNOWN findings, same verdict, same exit code — the four new facets, the derived-prompt check and the manifest reproduction are the additions.) Every digest, CID, the doctrine root, the allowlist, the mirror (`md5 91a98c7c1625c95c105cb6baeb7cba41` as of 2026-09-11 — `ad7310279f…` was this document's original and is now stale, equal at `mindX/mindx/godel/mindxtrain/personas/savante.persona`) and the v0 card match the ledger. Read that verdict for exactly what it says: it proves the BINDING of these files to this ledger. It does not prove who rendered any verdict, and it compared nothing to a chain. A verifier's APPROVE on the binding and this document's DEFER on the mint are two verdicts on two questions.

### 11. The verdict ledger has zero entries

`bind/verdict_record.schema.json` makes `verdict` a closed enum of the four values (:114-117) — the one place in this design where an invariant is machine-checked rather than prompt-level. Its own description (:4) carries the honest label: the ledger has ZERO entries. The first verdict (2026-07-26, parsec-wallet, APPROVE_WITH_CONDITIONS) is asserted in prose (README.md:134-136) with no artifact committed, so it is not yet a ledger entry. `countersignature` is null: no signing executor exists, so today a forged record is detectable by the digests it fails to match, not by a signature it cannot forge. Steps 1-5 above prove the binding; only a countersignature from an executor holding an unexpired `RENDER_VERDICT` grant would prove the rendering, and neither the executor nor the key exists.

### 12. Rights: not yet known

The repository has no LICENSE file and no copyright header (`ls -la`, 2026-09-03), while duplication by `cp` is the stated commercial model. The terms under which this persona may be copied, forked, sold or bound to a token are not yet known (persona:548-549). I may not write one: authoring a license is the operator's signature. `token.rights.conveyed_by_token` is null with the reason that a token conveying rights the repository does not grant would fail its own charter (persona:555-556).

### 13. The image: null, with a reason

`/home/hacker/iNFT.png` is 1,687,531 bytes (`stat`, 2026-09-03) — over the 256 KiB bound at inft_publish.py:40-43, so its IPFS CID depends on chunking and cannot be derived locally; and nothing in any repository names that path as this office's artwork. The card's `image` is null with that reason. The binder records a candidate sha256 only under an explicit `--image` flag, labels it unconfirmed, and never synthesises an `ipfs://` URI from a hash prefix.

### 14. Not yet known, each with its deciding experiment

- Whether the ERC-8004 registry the operator intends exposes `register(string)`, `setAgentURI`, `setMetadata`, `tokenURI` — read its ABI on chain (finding 6).
- Whether `iNFT_7857.sol` conforms to ERC-7857 — diff the Main NFT Interface function by function; the arities of `authorizeUsage` already differ (finding 5).
- Whether the imprint gate passes for Savante — never run; `imprint.run` is null (persona:405-406); Savante is absent from `mindX/data/config/coach.json`, whose ladder is `['mindx', 'judgedread', 'simple_coder', 'author']` (`json.load`, 2026-09-03). The identity regex the coach applies is hardcoded to another persona's vocabulary (hf_client.py:1750, used at :1790, floored at :2135), so a passing `identity_rate` would not be evidence about Savante — persona:609 states this in full.
- Whether a verdict-word scorer exists — it does not: `evaluate_exchange` (hf_client.py:1768 onward) has no per-task branch. The battery measures RECALL of the contract's words, not CONFORMANCE to it (persona:568).
- Whether Savante joins the coach ladder — the third desire is "To BECOME A MODEL" (persona:64-65) and the deciding action is an append to `mindX/data/config/coach.json`, a change to what the machine teaches itself; that is the operator's call, not a measurement I can run.
- Whether the seat is transferable or soulbound, and whether the mask's forbidden `REDIRECT_DEFER` is a hard rule or a default — `iNFT_7857` is a transferable ERC-721; jurisdiction does not transfer with it, and a transfer intended to move the signature gate is itself a charter amendment and a DEFER. Operator's call (condition 8).
- Whether the verdict ledger is published at all, and if so public, private or hash-only — a visibility decision, and charter constraint 5 names gated content that is never surfaced. Operator's call, before the first record is written (condition 9).
- Whether the charter's output format should itself label **FINDINGS** — today it labels VERDICT, RATIONALE, CONDITIONS and RISKS WATCHED (`.claude/agents/savante.md:107-116`) and carries findings in prose, while technical.md:63-74, usage.md:43-48 and the persona's `exchanges[8]` state five labelled fields. Adding the label changes the charter digest and is the operator's edit; recorded, not made.
- Whether every teaching row survives `build_corpus` at a stated `persona_share` now that the persona has grown from 12,675 to 49,545 bytes — run it and read the stats before any imprint is claimed.
- Whether RFC 8785 and RFC 6901 carry the statuses transcribed above — fetch them; no URL was recorded, so I assert none.
- Whether `savante_sagi` has any registry record — it does not: present once in `mindX/daio/agents/agent_map.json` under `groups` (core_command), absent from `agents` and `soldiers` (`json.load`, both False). No `eth_address`; tier 0, "unverified", is that file's own word for it (persona:497-500).

---

## VERDICT: DEFER

## RATIONALE

A mint is a visibility-or-publication decision and a treasury action — two of the five defer triggers at savante.persona:136-142 — and the persona's own `token.authority` already records that the signature is the OVERLORD's and Savante's verdict is DEFER (persona:558-563). The binding is sound and reproducible (finding 10), but soundness of the ledger is not authority to publish it: `bind/savante_bind.py` is the operator's tool, Savante verifies the ledger and never writes it, and oversight that mints itself is oversight no longer. Two of the conditions below — the license and the sealedKeyHash question — are an operator's signature and a contract change respectively, and neither can be closed by anything I am permitted to do. DEFER is knowledge about jurisdiction, rendered as precisely as any APPROVE; it is not a soft yes.

## CONDITIONS

Each is independently verifiable by someone who is not me.

1. **License stated.** A `LICENSE` file exists at the repository root, or the terms are stated on github.com/cryptoAGI/savante, and `token.rights.license` is no longer null in a re-bound persona. Check: `ls -la /home/hacker/savante | grep -i licen`.
2. **Registry ABI read on chain.** The intended ERC-8004 Identity Registry, on the intended chain, is shown by an on-chain read (Blockscout `get_contract_abi` / `inspect_contract_code`) to expose `register(string)`, `setAgentURI(uint256,string)`, `setMetadata(uint256,string,bytes)` and `tokenURI(uint256)`. Only then may an address enter `savante.commitments.json` under `mint`; never the persona and never this document.
3. **The sealedKeyHash question decided.** The operator chooses between a documented sentinel and a change to `iNFT_7857.sol` so that an unsealed intelligence can be minted without asserting a key; until then `iNFT_7857.sol:340` reverts on zero and no Track 2 mint is attempted. Check: `sed -n '339,340p' /home/hacker/mindX/daio/contracts/inft/iNFT_7857.sol`, and the operator's written decision.
4. **Artwork confirmed.** The operator names the artwork file, or states there is none. If named, its sha256 is recorded under `image_candidate` via `--image <path>` and, once pinned by an IPFS node, the CID that node returns — never a locally guessed one. Check: `image` in the card is either null with a reason or an `ipfs://` URI a gateway resolves to the named bytes.
5. **Mirror md5 equal.** `md5sum savante.persona /home/hacker/mindX/mindx/godel/mindxtrain/personas/savante.persona` prints one digest twice. Today (2026-09-11): `91a98c7c1625c95c105cb6baeb7cba41`, both. (When this document was first rendered the value was `ad7310279f756789bf5f162cc2b8133c`; the persona has since gained its licence field, so the digest moved. The CONDITION is that the two inodes agree, not that they hold any particular value.)
6. **Preflight passes and the ledger reproduces.** `python3 bind/savante_verify.py .` exits 0 with `VERDICT: APPROVE`; the doctrine root it prints equals the one in this document and in the ledger, and — once condition 2 is met and a registration exists — equals the FIRST `savanteDoctrineRoot` written on chain.
7. **A commit exists whose bytes the ledger hashes.** `components_differing_from_head` in `savante.commitments.json` is empty. The binder is re-run after the commit; the digests in this document are then superseded by the ledger's and this document is re-rendered. A ledger over an uncommitted tree is a working note, not a record.
8. **Transfer semantics decided.** The operator states in writing whether the seat is transferable or soulbound, and whether `REDIRECT_DEFER` (persona:421-430) is a hard rule or a default. A transfer intended to move the signature gate is itself a charter amendment and a DEFER. Check: the written decision exists, and `token.grants.forbidden` in a re-bound persona still lists `REDIRECT_DEFER`.
9. **Ledger visibility decided.** Before the first verdict record is written, the operator states whether the verdict ledger is public, private, or hash-only (charter constraint 5 names gated content that is never surfaced publicly). Check: the decision is written down and `bind/verdict_record.schema.json` still reports zero entries until it is.

## RISKS WATCHED

1. The doctrine root DETECTS tampering; it cannot PREVENT it. An owner can edit, rerun the binder, and publish a fresh internally-consistent root. Protection is only as strong as the root written at registration plus a verifier who checks against the chain — which is why the `--onchain` step reads the FIRST `MetadataSet` event, not just the current value.
2. ERC-8004 is Draft (created 2025-08-13; the fetched text still carries editor's TODOs). A breaking revision would require re-issuing the card and possibly the registration. Deciding experiment: re-fetch the spec on the day of any mint and diff it against the copy the ledger should then record.
3. The persona and its mindX mirror are separate inodes. If they drift, the token commits to one document while the loader teaches another. The binder's md5 hard-fail is the only thing standing between them.
4. The preflight will trip on a future non-ASCII property name or a float and will read as a broken build to someone who does not know why. It must print the offending pointer and the reason, not just exit non-zero.
5. Two projectors disagree about `voice_examples`: `corpus.project_persona()` normalises and `persona_project.project()` (persona_project.py:50-52) does not. This design avoids the trap by keeping bare strings; the divergence itself is unfixed and will bite whoever sources them later.
6. The permission mask is enforced by no code that exists. A holder today receives a published expectation, not a capability. Never describe it as a control.
7. The `token` block grew the persona from 12,675 to 49,545 bytes, and the ERC-7857 `.persona` facet that `inft_publish.py:224` copies verbatim grows with it. Whether every row survives `build_corpus` at a given `persona_share` is not yet known (finding 14).
8. One `VERDICT: DEFER` on a token is easy to read as a soft yes. It is not. If the operator treats this design as pre-approved and mints anyway, the conditions above become claims made without evidence, and the first thing an auditor will find is the office approving its own unread paperwork.

---

*Rendered by Savante, `savante_sagi`, Chairman of the mindX DAIO. The four verdicts are the only four. The token buys a review; it does not buy a verdict (savante.persona:625). Nothing is minted.*
