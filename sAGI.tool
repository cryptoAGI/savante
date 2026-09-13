{
  "$comment": "DERIVED from the charter frontmatter (.claude/agents/savante.md:10) and savante.persona #/token/intelligence/tool_allowlist + #/token/grants. Regenerable; never hand-edited. Spec: sagi/engine/FACET_BUNDLE.md §6.",
  "format": "sagi.tool/1",
  "id": "sAGI",
  "officer": "savante_sagi",

  "allowlist": [
    {"tool": "Read", "enforced_by": "harness", "source": ".claude/agents/savante.md:10"},
    {"tool": "Grep", "enforced_by": "harness", "source": ".claude/agents/savante.md:10"},
    {"tool": "Glob", "enforced_by": "harness", "source": ".claude/agents/savante.md:10"},
    {"tool": "Bash", "enforced_by": "harness", "source": ".claude/agents/savante.md:10"}
  ],
  "allowlist_note": "These four are the office. The harness refuses anything else because the frontmatter does not list it — a real control, at the only layer that has one. The same four are carried in the persona as pointer 15 of the doctrine root, so a holder can diff the two and see they agree.",

  "forbidden_tools": [
    {"tool": "Edit", "enforced_by": "harness", "consequence": "granting it voids the office"},
    {"tool": "Write", "enforced_by": "harness", "consequence": "granting it voids the office"},
    {"tool": "Agent", "enforced_by": "harness", "consequence": "granting it voids the office"}
  ],
  "forbidden_tools_note": "Read-only is not a promise this file makes; it is a property of the allowlist above. Oversight that edits what it audits is oversight no longer.",

  "grants": {
    "mechanism": "iNFT_7857.authorizeUsage(tokenId, executor, permissions, expiresAt) → UsageGrant{permissions, expiresAt, grantor} (mindX/daio/contracts/inft/iNFT_7857.sol:504-521)",
    "mask": [
      {"bit": "0x01", "name": "RENDER_VERDICT",  "enforced_by": "executor_that_does_not_exist"},
      {"bit": "0x02", "name": "READ_LEDGER",     "enforced_by": "executor_that_does_not_exist"},
      {"bit": "0x04", "name": "CI_GATE",         "enforced_by": "executor_that_does_not_exist"},
      {"bit": "0x08", "name": "STANDING_AUDIT",  "enforced_by": "executor_that_does_not_exist"},
      {"bit": "0x10", "name": "ADAPT_CANON",     "enforced_by": "executor_that_does_not_exist"}
    ],
    "forbidden": [
      {"name": "WRITE",             "enforced_by": "nothing"},
      {"name": "SIGN",              "enforced_by": "nothing"},
      {"name": "TRANSACT",          "enforced_by": "nothing"},
      {"name": "AMEND_CHARTER",     "enforced_by": "nothing"},
      {"name": "ADD_VERDICT_VALUE", "enforced_by": "nothing"},
      {"name": "REMOVE_DEFER",      "enforced_by": "nothing"},
      {"name": "ADD_EVIDENCE_CLASS","enforced_by": "nothing"},
      {"name": "REDIRECT_DEFER",    "enforced_by": "nothing"}
    ],
    "rule": "A grant setting any bit outside the mask is VOID — the executor refuses the whole grant rather than masking the extras, because silently ignoring an unauthorised bit teaches the holder to keep asking. There is no bit that buys an APPROVE.",
    "enforcement": "NOT A CONTROL. The chain stores the bitmap and never reads it: `uint256 permissions; // bitmap interpreted off-chain` (iNFT_7857.sol:124), and isUsageAuthorized (:531-535) returns true on expiry alone, reading no bit. The executor that would validate the bits does not exist. A holder receives a published expectation, never a capability. Deciding experiment: ship an executor that reads getUsageGrant and refuses on any out-of-mask bit, then re-grade every row above.",
    "published_expectation_not_control": true
  },

  "enforced_by_legend": {
    "harness": "the runtime refuses the call",
    "nothing": "published expectation only; no code checks it",
    "executor_that_does_not_exist": "a control is specified and the thing that would apply it has not been built"
  }
}
