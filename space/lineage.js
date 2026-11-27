// lineage.js — the Lineage room: Savante reviews mindX's training lineage (huggingface.co/datasets/PYTHAI/mindXascension)
// from the visitor's browser. The claim under review, one generation at a time, is "generation N is what its record
// says". The office recomputes what a browser can (the adapter's bytes against the sha256 the record and the Hub name),
// reports what the record asserts as an assertion, and leaves what it cannot check here as NOT YET KNOWN with its
// deciding experiment. Public GETs only; no write path. Shared by both editions. Every string from the Hub is written
// with textContent.
import { sha256Hex, makeFinding, renderVerdict } from "./savante.js";

const DATASET = "PYTHAI/mindXascension";
const BASE = `https://huggingface.co/datasets/${DATASET}`;
const RAW = `${BASE}/resolve/main/`;
const $ = (id) => document.getElementById(id);
let DOC = null, ROWS = [], PICK = null, LAST = null;
const RESULTS = new Map();   // generation → { adapter: "agrees" | "DISAGREES" | "absent" | "unrecorded", verdict }

function td(text, cls) { const c = document.createElement("td"); c.textContent = text ?? "—"; if (cls) c.className = cls; return c; }
const sign = (x) => (typeof x === "number" ? (x >= 0 ? "+" : "") + x.toFixed(4) : "—");
async function getJSON(path) {
  const r = await fetch(RAW + path, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.json();
}
async function getBytes(path) {
  const r = await fetch(RAW + path, { cache: "no-store" });
  if (!r.ok) throw new Error(`${path}: HTTP ${r.status}`);
  return r.arrayBuffer();
}

function draw() {
  const f = $("lnfilter").value, q = $("lnq").value.trim();
  const tb = $("lnrows");
  tb.replaceChildren();
  for (const g of ROWS) {
    if (f !== "all" && g.verdict !== f) continue;
    if (q && !String(g.generation).startsWith(q.replace(/^gen/i, ""))) continue;
    const res = RESULTS.get(g.generation) || {};
    const tr = document.createElement("tr");
    tr.classList.add("pick");
    if (PICK === g.generation) tr.classList.add("sel");
    tr.title = "review this generation";
    const gate = g.verdict === "accepted" ? "ok" : g.verdict === "refused" ? "warn" : g.verdict === "failed" ? "bad" : "";
    const ad = res.adapter === "agrees" ? "ok" : res.adapter === "DISAGREES" ? "bad" : res.adapter ? "warn" : "";
    const sv = res.verdict === "REJECT" ? "bad" : res.verdict === "DEFER" ? "warn" : res.verdict ? "ok" : "";
    tr.append(td("gen" + g.generation), td(g.verdict, gate), td(sign(g.delta)),
              td(g.adapter_public ? "on the Hub" : g.adapter ? "private repo only" : "none"),
              td(g.merged_complete ? "complete" : "—"), td(res.adapter || "not recomputed", ad), td(res.verdict || "—", sv));
    tr.addEventListener("click", () => { PICK = g.generation; draw(); review(g); });
    tb.append(tr);
  }
}

async function readLineage() {
  $("lnnote").textContent = `reading ${DATASET}/LINEAGE.json…`;
  try {
    DOC = await getJSON("LINEAGE.json");
  } catch (e) {
    $("lnnote").textContent = `LINEAGE.json is not readable yet (${e.message}). Nothing can be reviewed until it is.`;
    return;
  }
  ROWS = (DOC.generations || []).slice().sort((a, b) => b.generation - a.generation);
  const c = DOC.counts || {}, p = DOC.policy || {}, ch = DOC.chain || {};
  $("lnnote").textContent = `${c.generations ?? ROWS.length} generations · accepted ${c.accepted ?? "?"} · refused ${c.refused ?? "?"} · ` +
    `failed ${c.failed ?? "?"} · on the Hub ${c.on_hub ?? "?"} of ${p.hub_keep ?? 99} kept · ` +
    `chain: ${ch.status === "not_deployed" ? "not yet deployed" : ch.status || "unstated"} · ` +
    `document built ${DOC.ts ? new Date(DOC.ts * 1000).toISOString().slice(0, 16).replace("T", " ") + " UTC" : "at an unstated time"}` +
    " — what the document says is an assertion until a row is reviewed.";
  draw();
}

// One generation, in the five-field contract.
async function review(g) {
  const n = g.generation;
  const out = $("lnout");
  out.textContent = `reviewing gen${n}: reading RECORD.json…`;
  const findings = [];
  let rec = null;
  try {
    rec = await getJSON(`weights/gen${n}/RECORD.json`);
    findings.push(makeFinding(`gen${n} has a record on the Hub`, `${BASE}/blob/main/weights/gen${n}/RECORD.json`, "known"));
  } catch (e) {
    findings.push(makeFinding(`gen${n} has a record on the Hub`, e.message, "not yet known",
      `run mindX scripts/hf_complete_lineage.py --execute --gens ${n}, then re-read weights/gen${n}/RECORD.json`));
  }
  const files = (rec && rec.files) || {};
  const s = (rec && rec.summary) || {};
  let adapterState = "absent";
  if (files.adapter_path) {
    out.textContent = `reviewing gen${n}: fetching the adapter (${files.adapter_bytes ? (files.adapter_bytes / 1e6).toFixed(1) + " MB" : "size unstated"}) and hashing it in this browser…`;
    try {
      const sha = await sha256Hex(await getBytes(files.adapter_path));
      const want = String(files.adapter_sha256 || "").toLowerCase();
      if (!want) {
        adapterState = "unrecorded";
        findings.push(makeFinding(`the adapter is the one the record names`, `recomputed sha256 ${sha}; the record names no sha256`,
          "not yet known", "rewrite the record with the Hub's LFS sha256 (hf_complete_lineage.py --records) and review again"));
      } else if (want === sha) {
        adapterState = "agrees";
        findings.push(makeFinding(`the adapter on the Hub is the adapter the record names`,
          `${files.adapter_path}: sha256 ${sha}, recomputed here from the bytes, equals the record's`, "known"));
      } else {
        adapterState = "DISAGREES";
        findings.push(makeFinding(`the adapter on the Hub is the adapter the record names`,
          `${files.adapter_path}: recomputed sha256 ${sha} ≠ the record's ${want}`, "known"));
      }
    } catch (e) {
      findings.push(makeFinding(`the adapter is readable`, e.message, "not yet known", `re-read ${files.adapter_path} when the Hub answers`));
    }
  } else if (rec) {
    const noWeights = g.verdict === "failed";
    adapterState = noWeights ? "none (failed run)" : "absent";
    findings.push(makeFinding(noWeights ? `gen${n} produced no weights, as its record says (stage ${s.stage || g.stage})`
      : `gen${n}'s adapter is on the public dataset`, noWeights ? `no adapter under weights/gen${n}/checkpoint/ on the Hub`
      : `the record names no adapter path`, noWeights ? "known" : "not yet known",
      noWeights ? "" : `copy the adapter from the private model repo onto the dataset and review again`));
  }
  if (rec) {
    findings.push(makeFinding(`the ascent log records gen${n} as ${s.verdict || g.verdict} (stage ${s.stage || g.stage}, imprint Δ ${sign(s.delta ?? g.delta)}, recall ${s.recall_before ?? "—"} → ${s.recall_after ?? "—"})`,
      `RECORD.json rows, projected from mindX data/logs/ascend_log.jsonl — this is what the log says, read, not recomputed`, "known"));
    if (typeof (s.delta ?? g.delta) === "number") {
      findings.push(makeFinding(`the imprint result reproduces`, `not recomputable in a browser (it needs the model run on the recall battery)`,
        "not yet known", `re-run mindXtrain imprint for gen${n} against its base on the battery in machine.dream/MANIFEST.json; it reproduces if Δ lands within ±0.03 of ${sign(s.delta ?? g.delta)}`));
    }
    if (files.merged_path) {
      findings.push(makeFinding(`the merged weights are base + this adapter`, `${files.merged_path}, sha256 ${files.merged_sha256 || "unrecorded"}; 269 MB, not rebuilt here`,
        "not yet known", `rebuild with peft merge_and_unload (fp32 → bf16) from ${(rec.files.merged_rebuilt || {}).base || "HuggingFaceTB/SmolLM2-135M"} and compare sha256`));
    }
  }
  const chain = (DOC && DOC.chain) || {};
  findings.push(makeFinding(`gen${n} is anchored on a blockchain`, chain.note || "LINEAGE.json states no anchor",
    "not yet known", "deploy the per-generation iNFT/THOT anchor, then read the anchor back and compare it with the record's hashes"));

  const disagree = adapterState === "DISAGREES";
  const noRecord = !rec;
  const verdict = disagree ? "REJECT" : noRecord || adapterState === "absent" ? "DEFER" : "APPROVE_WITH_CONDITIONS";
  const conditions = [
    typeof (s.delta ?? g.delta) === "number" ? `The imprint for gen${n} is re-run and lands within ±0.03 of ${sign(s.delta ?? g.delta)}.` : null,
    files.merged_path ? `The merged weights are rebuilt from base + adapter and their sha256 equals ${String(files.merged_sha256 || "the record's").slice(0, 16)}….` : null,
    `A chain anchor for gen${n} exists and reads back the same hashes.`,
  ].filter(Boolean).join("\n");
  const rationale = disagree
    ? `The adapter's bytes do not hash to the value the record names. A record that does not describe its own artefact cannot stand.`
    : noRecord ? `There is no record to review against. The office defers until one exists.`
    : adapterState === "absent" ? `The record exists but the weights it would describe are not on the public dataset, so the claim cannot be checked.`
    : `What a browser can recompute agrees with the record. What it cannot recompute — the imprint, the merge, the anchor — is stated as not yet known, each with the experiment that would decide it.`;
  const v = renderVerdict({ target: `mindX lineage gen${n}: "generation ${n} is what its record says" (${DATASET})`,
    findings, verdict, rationale, conditions,
    risks: "A record written by the same system that trained the model; the Hub's LFS metadata as the hash source; no signature on any of it." });
  LAST = { n, verdict, text: v.text };
  RESULTS.set(n, { adapter: adapterState, verdict });
  out.textContent = v.text;
  const title = encodeURIComponent(`Savante review: gen${n} — ${verdict}`);
  const body = encodeURIComponent(v.text.slice(0, 1800) + (v.text.length > 1800 ? "\n…" : "") + `\n\nReviewed in the browser at huggingface.co/spaces/PYTHAI/savante#lineage`);
  const a = $("lnpublic");
  a.href = `${BASE}/discussions/new?title=${title}&description=${body}`;
  a.hidden = false;
  draw();
}

async function reviewAll() {
  const btn = $("lnall");
  btn.disabled = true;
  const todo = ROWS.filter((g) => g.adapter_public);
  let i = 0;
  for (const g of todo) {
    i++;
    btn.textContent = `recomputing ${i} of ${todo.length}…`;
    PICK = g.generation;
    await review(g);
  }
  const t = { agrees: 0, DISAGREES: 0, other: 0 };
  for (const r of RESULTS.values()) t[r.adapter === "agrees" || r.adapter === "DISAGREES" ? r.adapter : "other"]++;
  btn.textContent = `recomputed: ${t.agrees} agree · ${t.DISAGREES} disagree · ${t.other} unverified`;
  btn.disabled = false;
}

if ($("lnrows")) {   // only on a page that has the room
  $("lngo").addEventListener("click", readLineage);
  $("lnall").addEventListener("click", reviewAll);
  $("lnfilter").addEventListener("change", draw);
  $("lnq").addEventListener("input", draw);
  let read = false;
  const room = document.querySelector('[data-room="lineage"]');
  const first = () => { if (read || room.hidden) return; read = true; readLineage(); };
  new MutationObserver(first).observe(room, { attributes: true, attributeFilter: ["hidden"] });
  first();
}
