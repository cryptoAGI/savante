// SPDX-License-Identifier: MIT
// cpu.cluster — visitors' browsers lending savanteML to a dmind host (distributed.mind), measured in inference terms.
//
//   CONTRIBUTE → join (the realm token names the wallet credited) → pull a job (long-poll) → run it here on savanteML,
//   exactly as sent → send the answer and its receipt (the host checks sha256(answer) against it) → rest → pull …
//
// The host measures what this browser gave as ITE (dmind 1.7.0: one token through a 1B-parameter model; a job's ITE =
// (prompt + completion tokens) × params / 1e9, from the receipt's host-bounded counts), beside core-, GPU- and RAM
// GB-seconds; a host may pay it per kITE in BANKON PAI (paymint; a USD basket of USDC, USDT and DAI / USDS at 18 decimals). The page never signs anything: COLLECT returns
// vouchers the contributor sends from their own wallet.
//
// Safety, as browseML's SHARE keeps it: the realm token goes ONLY to the host's own same-origin paths. CONTRIBUTE is
// enabled only when this page is served by the dmind host itself (savante-host.json beside it names the paths and the
// token's storage key). Anywhere else (huggingface.co) the room shows the public pool and this browser's measurement,
// and links to the host's own copy of the room. Nothing is shared until CONTRIBUTE is pressed; STOP ends it at once.
import * as sml from "./savanteml.js";

const $ = (id) => document.getElementById(id);
const PUBLIC_HOST = "https://mindx.pythai.net";
const HOST_ROOM = `${PUBLIC_HOST}/savante/office/#cluster`;
const PATHS = ["join", "update", "pull", "result", "leave", "me", "collect"];
const HEARTBEAT_MS = 30_000, ERROR_BACKOFF_MS = 15_000, PAUSE_POLL_MS = 5_000;
const KEY = "savante.cluster";

let host = null;            // savante-host.json, when this page is the host's own copy
const st = { phase: "off", why: "", session: "", jobs: 0, refused: 0, ite: 0, tokens: 0, engineMs: 0, thoughts: [] };
let ctl = null;
const settings = (() => { try { return { pct: 25, maxJobTokens: 256, onlyVisible: true, ...JSON.parse(localStorage.getItem(KEY) || "{}") }; } catch { return { pct: 25, maxJobTokens: 256, onlyVisible: true }; } })();
const saveSettings = () => { try { localStorage.setItem(KEY, JSON.stringify(settings)); } catch { /* per-viewer convenience */ } };

const local = (p) => typeof p === "string" && p.startsWith("/") && !p.startsWith("//");
async function readHost() {
  try {
    const r = await fetch("savante-host.json", { cache: "no-store" });
    if (!r.ok) return null;
    const h = await r.json(), sh = h && h.share;
    // the same rule as browseML's parseHost: every share path same-origin, and a token key to read it from
    if (!sh || !PATHS.every((k) => local(sh[k])) || typeof sh.token !== "string" || !sh.token) return null;
    return { label: String(h.label || "the host"), insight: local(sh.insight) ? sh.insight : "/insight/sharedcpu", signin: local(sh.signin) ? sh.signin : null, ...sh };
  } catch { return null; }
}
const token = () => { try { return localStorage.getItem(host.token) || ""; } catch { return ""; } };

async function call(path, body, keepalive = false, signal) {
  const r = await fetch(host[path], { method: "POST", credentials: "omit", keepalive, signal,
    headers: { Authorization: `Bearer ${token()}`, "Content-Type": "application/json", Accept: "application/json" }, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (j && j.barred) throw Object.assign(new Error(j.reason || "the host refuses this wallet"), { final: true });
  if (!r.ok) throw new Error(`the host says ${r.status}${j && j.detail ? `: ${j.detail}` : ""}`);
  return j;
}
const sleep = (ms, signal) => new Promise((res) => { const t = setTimeout(res, ms); signal && signal.addEventListener("abort", () => { clearTimeout(t); res(); }, { once: true }); });

// ── what is shown ───────────────────────────────────────────────────────────────────────────────────────────────
function row(dl, k, v) {
  const dt = document.createElement("dt"); dt.textContent = k;
  const dd = document.createElement("dd"); dd.textContent = v;
  dl.append(dt, dd);
}
function draw() {
  const live = $("clstate");
  if (!live) return;
  const label = { off: "not contributing", starting: "starting…", waiting: "waiting for a job", working: "computing a job",
    resting: "resting (your share)", paused: "paused", error: "stopped by an error" }[st.phase] || st.phase;
  live.textContent = label + (st.why ? ` — ${st.why}` : "");
  live.className = "pstate " + (st.phase === "working" || st.phase === "waiting" ? "ok" : st.phase === "error" ? "bad" : "");
  const go = $("clgo");               // absent on a copy that is not the host's (it is a link there)
  if (go) go.textContent = st.phase === "off" || st.phase === "error" ? "Contribute" : "STOP";
  const dl = $("clvisit"); dl.textContent = "";
  row(dl, "jobs this visit", `${st.jobs} accepted · ${st.refused} refused`);
  row(dl, "tokens computed", String(st.tokens));
  row(dl, "ITE computed (this visit)", st.ite.toFixed(2));
  row(dl, "engine time", `${(st.engineMs / 1000).toFixed(1)} s`);
  const ol = $("clthoughts"); ol.textContent = "";
  for (const t of st.thoughts) {
    const li = document.createElement("li");
    li.textContent = `${new Date(t.at).toLocaleTimeString()} · ${t.kind} · ${t.purpose || "—"} · ${t.tokens} tokens · ${(t.ms / 1000).toFixed(1)} s · ${t.verdict}`;
    ol.append(li);
  }
}

async function readPool() {
  const out = $("clpool"); if (!out) return;
  const url = host ? host.insight : `${PUBLIC_HOST}/insight/sharedcpu`;
  out.textContent = "reading the pool…";
  try {
    const ctl2 = new AbortController(); const t = setTimeout(() => ctl2.abort(), 15000);
    const r = await fetch(url, { credentials: "omit", headers: { Accept: "application/json" }, signal: ctl2.signal });
    clearTimeout(t);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const j = await r.json();
    out.textContent = "";
    const dl = document.createElement("dl"); dl.className = "kv";
    row(dl, "contributors now", `${j.contributors ?? "?"} (${j.available ?? "?"} available, ${j.queued ?? 0} jobs queued)`);
    if (j.totals) {
      row(dl, "given in all", `${Number(j.totals.core_seconds || 0).toFixed(0)} core-seconds · ${Number(j.totals.gpu_seconds || 0).toFixed(0)} GPU-seconds`);
      if (j.totals.ite != null) row(dl, "ITE in all", Number(j.totals.ite).toFixed(1));
    }
    row(dl, "trusted after", `${j.trust_after ?? "?"} passed audits`);
    row(dl, "read", `${new Date().toISOString()} from ${url}`);
    out.append(dl);
  } catch (e) {
    const why = e?.name === "AbortError" ? "no answer within 15 s" : String(e?.message || e).slice(0, 120);
    out.textContent = `the dmind host did not answer (${why}) at ${url}. ` +
      (host ? "" : "mindx.pythai.net is the cluster's host; while it is unreachable, nothing can be contributed. ") +
      "This browser's measurement below still works: it runs here.";
  }
}

async function measure(runBench = true) {
  const out = $("clbench");
  out.textContent = "";
  const dl = document.createElement("dl"); dl.className = "kv"; out.append(dl);
  row(dl, "threads savanteML can use", `${sml.threads()} (${globalThis.crossOriginIsolated ? "cross-origin isolated" : "one thread: this page is not cross-origin isolated"})`);
  row(dl, "memory this browser reports", navigator.deviceMemory ? `≥ ${navigator.deviceMemory} GB` : "not reported");
  let gpu = "no WebGPU";
  try { const a = navigator.gpu && await navigator.gpu.requestAdapter(); if (a) { const i = a.info || (a.requestAdapterInfo ? await a.requestAdapterInfo() : {}); gpu = `WebGPU: ${[i.vendor, i.architecture, i.device].filter(Boolean).join(" ") || "an adapter"} (savanteML computes on the CPU; the GPU is reported, not used)`; } } catch { /* none */ }
  row(dl, "graphics", gpu);
  if (!runBench) { row(dl, "speed", "press Measure: it runs a short prompt on savanteML here"); return null; }
  if (!sml.isReady() && !(await sml.isCached())) {
    row(dl, "speed", `not measured: load savanteML first (${(sml.MODEL.bytes / 1e6).toFixed(0)} MB once, verified before it answers)`);
    return null;
  }
  row(dl, "speed", "measuring on a short prompt…");
  try {
    const b = await sml.bench();
    dl.lastChild.textContent = `${b.prompt_tps?.toFixed(1) ?? "?"} prompt tokens/s · ${b.gen_tps?.toFixed(2) ?? "?"} generated tokens/s · receipt ${b.ok ? "✓" : "✗"}`;
    const perHour = (b.gen_tps || 0) * 3600 * (settings.pct / 100) * sml.PARAMS / 1e9;
    row(dl, "projection at your share", `≈ ${perHour.toFixed(0)} ITE an hour at ${settings.pct}% (generation only; a projection, not a measurement — the host measures what is paid)`);
    return b;
  } catch (e) { dl.lastChild.textContent = `could not measure: ${String(e?.message || e).slice(0, 160)}`; return null; }
}

async function readMe() {
  const out = $("clme"); if (!out || !host) return;
  if (!token()) { out.textContent = "sign in on the host to see what your wallet has given."; return; }
  try {
    const r = await fetch(host.me, { credentials: "omit", headers: { Authorization: `Bearer ${token()}`, Accept: "application/json" } });
    const j = await r.json();
    out.textContent = "";
    const dl = document.createElement("dl"); dl.className = "kv";
    const eq = j.equivalence;
    if (eq) {
      row(dl, "ITE matured", `${Number(eq.ite_matured).toFixed(2)} (${eq.kite_matured} kITE)`);
      row(dl, "ITE pending (inside the audit window)", Number(eq.ite_pending).toFixed(2));
      const rs = eq.resources || {};
      row(dl, "resources given", `${rs.core_seconds ?? 0} core-s · ${rs.gpu_seconds ?? 0} GPU-s · ${rs.ram_gb_seconds ?? 0} RAM GB·s · ${rs.prompt_tokens ?? 0} + ${rs.completion_tokens ?? 0} tokens`);
    } else row(dl, "ITE", "this host does not measure ITE yet (dmind 1.7.0)");
    if (j.trust) row(dl, "trust", `${j.trust.passed ?? 0} of ${j.trust.after ?? "?"} audits passed${j.trust.trusted ? " · trusted" : ""}`);
    const p = j.payout;
    if (p && !p.error) for (const a of p.assets || []) row(dl, `${a.label} (${a.role})`, `${a.due_wei} base units due · ${a.paid_tokens} ${p.unit || "token"}s paid`);
    else row(dl, "paymint", "off: BANKON PAI is not deployed yet, so nothing is payable; your ITE is still measured and kept");
    out.append(dl);
  } catch (e) { out.textContent = `the host did not answer: ${String(e?.message || e).slice(0, 120)}`; }
}

async function collect() {
  const out = $("clvouchers");
  out.textContent = "asking the host for vouchers…";
  try {
    const j = await call("collect", {});
    out.textContent = j.vouchers?.length
      ? "Send these from your own wallet (redeemWithSignature, or redeemBatch for several). This page signs nothing and sends nothing.\n\n" + JSON.stringify(j.vouchers, null, 1)
      : "nothing due yet: ITE becomes payable once it has matured past the audit window, in whole kITE.";
  } catch (e) { out.textContent = String(e?.message || e).slice(0, 200); }
}

// ── the loop ────────────────────────────────────────────────────────────────────────────────────────────────────
async function join(speeds) {
  const v = sml.info();
  const j = await call("join", { model: v.model, model_sha256: v.sha256, threads: v.threads, share_pct: settings.pct,
    max_job_tokens: settings.maxJobTokens, engine: `${sml.ENGINE}/${v.version}`, contributor: "browser",
    ...(speeds?.gen_tps ? { gen_tps: speeds.gen_tps } : {}), ...(speeds?.prompt_tps ? { prompt_tps: speeds.prompt_tps } : {}) });
  if (!j.ok) throw Object.assign(new Error(j.reason || "the host refused"), { final: true });
  st.session = j.session;
}

async function start() {
  if (ctl || !host) return;
  if (!token()) { st.phase = "error"; st.why = "sign in on the host first"; draw(); if (host.signin) location.href = host.signin; return; }
  ctl = new AbortController(); const signal = ctl.signal;
  st.phase = "starting"; st.why = ""; draw();
  try {
    await sml.ensure((got, total, phase) => { st.why = phase === "download" ? `downloading the model ${(100 * got / total).toFixed(0)}%` : phase; draw(); });
    const speeds = await sml.bench().catch(() => null);
    await join(speeds);
  } catch (e) { st.phase = "error"; st.why = String(e?.message || e); ctl = null; draw(); return; }
  let beat = Date.now(), restUntil = 0;
  while (!signal.aborted) {
    try {
      if (settings.onlyVisible && document.hidden) {
        if (st.phase !== "paused") { await call("update", { session: st.session, paused: true }); beat = Date.now(); }
        st.phase = "paused"; st.why = "this tab is hidden (your choice)"; draw();
        if (Date.now() - beat > HEARTBEAT_MS) { beat = Date.now(); await call("update", { session: st.session }); }
        await sleep(PAUSE_POLL_MS, signal); continue;
      }
      if (Date.now() < restUntil) { st.phase = "resting"; st.why = ""; draw(); await sleep(Math.min(PAUSE_POLL_MS, restUntil - Date.now()), signal); continue; }
      st.phase = "waiting"; st.why = ""; draw();
      const got = await call("pull", { session: st.session }, false, signal); beat = Date.now();
      if (!got.ok) { if (/no such session|session closed/.test(String(got.reason))) { await join(); continue; } throw new Error(got.reason || "pull refused"); }
      if (!got.job) continue;
      const job = got.job;
      st.phase = "working"; st.why = `${job.kind_label || job.kind}: ${job.purpose || ""}`.slice(0, 160); draw();
      let withdrawn = false;
      const alive = setInterval(() => {
        call("update", { session: st.session }).then((b) => { if (b?.cancelled === job.job) { withdrawn = true; sml.abort(); } }).catch(() => {});
      }, HEARTBEAT_MS);
      const t0 = performance.now();
      let a = null;
      try { a = await sml.run(job); } catch (e) { if (!withdrawn && !signal.aborted) throw e; }
      finally { clearInterval(alive); beat = Date.now(); }
      const ms = performance.now() - t0; st.engineMs += ms;
      if (signal.aborted) break;                       // STOP mid-job: nothing sent; leave returns the job to the queue
      if (withdrawn || !a) { st.thoughts = [{ at: Date.now(), kind: job.kind, purpose: job.purpose, tokens: 0, ms, verdict: "withdrawn" }, ...st.thoughts].slice(0, 12); continue; }
      if (!a.ok) throw new Error("this browser's own receipt check failed: the answer is not sent");
      const r = await call("result", { session: st.session, job: job.job, text: a.text, receipt: a.receipt, usage: a.usage, timings: a.timings });
      const tokens = (a.usage.prompt_tokens || 0) + (a.usage.completion_tokens || 0);
      if (r.ok) { st.jobs++; st.tokens += tokens; st.ite += sml.ite(a.usage.prompt_tokens, a.usage.completion_tokens); } else st.refused++;
      st.thoughts = [{ at: Date.now(), kind: job.kind_label || job.kind, purpose: job.purpose, tokens, ms,
        verdict: !r.ok ? `refused: ${r.reason || ""}` : r.audit === "held" ? "held for audit" : "accepted" }, ...st.thoughts].slice(0, 12);
      restUntil = Date.now() + ms * (100 / Math.max(5, settings.pct) - 1);   // your share: rest so the engine runs pct% of the time
      draw(); readMe();
    } catch (e) {
      if (signal.aborted) break;
      st.phase = "error"; st.why = String(e?.message || e).slice(0, 200); draw();
      if (e.final) { ctl = null; st.session = ""; break; }
      await sleep(ERROR_BACKOFF_MS, signal);
    }
  }
}

async function stop() {
  const c = ctl; ctl = null;
  c && c.abort();
  sml.abort();
  const s = st.session; st.session = "";
  st.phase = "off"; st.why = ""; draw();
  if (s && host) { try { await call("leave", { session: s }, true); } catch { /* the host expires it */ } }
}

// ── boot ────────────────────────────────────────────────────────────────────────────────────────────────────────
async function boot() {
  if (!$("clgo")) return;
  host = await readHost();
  $("clwhere").textContent = host
    ? `This page is ${host.label}'s own copy: contributing sends your realm token to ${location.origin} only.`
    : `Contributing needs the host's own copy of this room, so your realm token never leaves the host's origin: ${HOST_ROOM}`;
  if (!host) {
    const a = document.createElement("a"); a.href = HOST_ROOM; a.target = "_blank"; a.rel = "noopener"; a.textContent = "open the cluster on the host";
    $("clgo").replaceWith(a); a.className = "primary"; a.id = "clgo-link";
    $("clmewrap").hidden = true;
  } else {
    $("clgo").addEventListener("click", () => (ctl ? stop() : start()));
    $("clcollect").addEventListener("click", collect);
    readMe();
  }
  $("clpct").value = settings.pct; $("clpctv").textContent = `${settings.pct}%`;
  $("clpct").addEventListener("input", (e) => { settings.pct = Math.max(5, Math.min(100, Number(e.target.value))); $("clpctv").textContent = `${settings.pct}%`; saveSettings(); if (st.session) call("update", { session: st.session, share_pct: settings.pct }).catch(() => {}); });
  $("cltok").value = String(settings.maxJobTokens);
  $("cltok").addEventListener("change", (e) => { settings.maxJobTokens = Number(e.target.value); saveSettings(); if (st.session) call("update", { session: st.session, max_job_tokens: settings.maxJobTokens }).catch(() => {}); });
  $("clvis").checked = !!settings.onlyVisible;
  $("clvis").addEventListener("change", (e) => { settings.onlyVisible = e.target.checked; saveSettings(); });
  $("clmeasure").addEventListener("click", async () => {
    if (!sml.isReady() && !(await sml.isCached())) {
      $("clbench").textContent = "loading savanteML…";
      try { await sml.ensure((g, t, ph) => { $("clbench").textContent = ph === "download" ? `downloading the model: ${(100 * g / t).toFixed(0)}% of ${(t / 1e6).toFixed(0)} MB` : `${ph}…`; }); }
      catch (e) { $("clbench").textContent = `savanteML could not load: ${String(e?.message || e).slice(0, 160)}`; return; }
    }
    measure();
  });
  addEventListener("pagehide", () => { if (ctl) stop(); });
  draw();
  // read the pool when the room is first opened
  const room = document.querySelector('[data-room="cluster"]');
  let read = false;
  const look = () => { if (!read && room && !room.hidden) { read = true; readPool(); measure(false); } };
  new MutationObserver(look).observe(room, { attributes: true, attributeFilter: ["hidden"] });
  look();
}
boot();
