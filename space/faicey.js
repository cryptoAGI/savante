// faicey.js — the embodied office: voaicey speaks, the mouth is an oscilloscope of what is actually playing,
// the eye is the visitor's camera, the ear is the visitor's microphone. The controls sit on the machine side.
//
// Lineage: the scope is the edge-triggered trace of DeltaVerse ollywoo/mouth.js (© Professor Codephreak, MIT),
// redrawn as a mouth; the voaicey call follows ollywoo/voicey.js (fetch → blob → <audio> → AnalyserNode, so
// X-Voaice-Backend can be read and the samples are same-origin); the getUserMedia handling follows
// ollywoo.html. Nothing is imported from those trees at run time.
//
// Standing rules, the same as the rest of the page:
//   * NO SIGNAL, NO PICTURE. When nothing is playing the trace is flat; when the browser voice is the only tier
//     available it exposes no samples, so the mouth draws a labelled envelope and says "not measured".
//   * Nothing is recorded, uploaded or analysed beyond the level drawn here. Leaving the room stops the camera
//     and the microphone.
//   * A render, not a measurement: sAGI.faice and sAGI.voaice keep faceprint and voiceprint null, and nothing
//     here computes or displays one.
//   * Every string from the network is written with textContent.

const $ = (id) => document.getElementById(id);
export const FREE_TEXT_MAX = 240;   // the voicey server's VOAICE_VOICEY_FREETEXT_MAX; above it the server returns 413
const FALLBACK_VOICES = ["M1", "M2", "M3", "M4", "M5", "F1", "F2", "F3", "F4", "F5"];

const S = {
  actx: null, gain: null, speakAn: null, micAn: null,
  audio: null, blobUrl: null, backend: "—", tier: "idle",
  envelope: 0, envelopeOn: false,
  cam: null, mic: null, micSrc: null,
  raf: 0, visible: false, lastErr: "",
};

// ── voicey request, exactly the server's contract ─────────────────────────────
export function voiceyUrl(endpoint, { persona = "savante", voice = "", text = "" } = {}) {
  const u = new URL(String(endpoint || "").trim());
  if (!/^https?:$/.test(u.protocol)) throw new Error("the endpoint must be http(s)");
  u.searchParams.set("persona", String(persona || "savante").trim() || "savante");
  const t = String(text || "").trim();
  if (t) u.searchParams.set("text", fitLine(t));   // capped here, so the server never has to refuse it
  if (voice) u.searchParams.set("voice", voice);
  return u.toString();
}

// Fit a line to the server's cap at a sentence (or word) boundary rather than mid-word.
export function fitLine(text, max = FREE_TEXT_MAX) {
  const t = String(text || "").replace(/\s+/g, " ").trim();
  if (t.length <= max) return t;
  const cut = t.slice(0, max);
  const end = Math.max(cut.lastIndexOf(". "), cut.lastIndexOf("; "), cut.lastIndexOf("? "), cut.lastIndexOf("! "));
  if (end > max * 0.4) return cut.slice(0, end + 1);
  const sp = cut.lastIndexOf(" ");
  return sp > 0 ? cut.slice(0, sp) : cut;
}

function ctx() {
  if (!S.actx) {
    const AC = window.AudioContext || window.webkitAudioContext;
    S.actx = new AC();
    S.gain = S.actx.createGain();
    S.gain.gain.value = +$("fc_gain").value || 1;
    S.speakAn = S.actx.createAnalyser();
    S.speakAn.fftSize = 2048;
    S.speakAn.smoothingTimeConstant = 0.6;
    S.gain.connect(S.speakAn);
    S.speakAn.connect(S.actx.destination);
  }
  if (S.actx.state === "suspended") S.actx.resume();
  return S.actx;
}

function stopSpeaking() {
  if (S.audio) { try { S.audio.pause(); } catch {} S.audio = null; }
  if (S.blobUrl) { URL.revokeObjectURL(S.blobUrl); S.blobUrl = null; }
  try { speechSynthesis.cancel(); } catch {}
  S.envelopeOn = false; S.envelope = 0;
  S.tier = "idle";
  led("fc_led_voice", "");
  readout();
}

async function speak(text) {
  stopSpeaking();
  ctx();
  const endpoint = $("fc_url").value;
  const persona = $("fc_persona").value;
  const voice = $("fc_voice").value;
  let url;
  try { url = voiceyUrl(endpoint, { persona, voice, text }); }
  catch (e) { S.lastErr = String(e.message || e); readout(); return; }
  S.tier = "voaicey · fetching";
  led("fc_led_voice", "warn");
  readout();
  try {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), 20000);   // one synthesis slot on the server; do not wait forever
    const r = await fetch(url, { mode: "cors", credentials: "omit", signal: ac.signal }).finally(() => clearTimeout(timer));
    if (!r.ok) {
      let detail = "";
      try { detail = (await r.clone().json()).error || ""; } catch {}
      throw new Error(`voicey HTTP ${r.status}${detail ? " — " + detail : ""}`);
    }
    S.backend = r.headers.get("X-Voaice-Backend") || "voaice (backend header not exposed to this origin)";
    S.blobUrl = URL.createObjectURL(await r.blob());   // same-origin bytes: the analyser may read them
    const el = new Audio();
    el.src = S.blobUrl;
    S.actx.createMediaElementSource(el).connect(S.gain);
    S.audio = el;
    el.onended = () => { if (S.audio === el) { S.tier = "idle"; led("fc_led_voice", ""); readout(); } };
    await el.play();
    S.tier = "voaicey · samples";
    S.lastErr = "";
    led("fc_led_voice", "on");
  } catch (e) {
    // CORS refusal, 429/502/503, or offline. Say which, then speak through the browser — which exposes no samples.
    S.lastErr = e && e.name === "AbortError" ? "voicey did not answer within 20 s (its one synthesis slot may be busy)"
      : /Failed to fetch|NetworkError|TypeError/i.test(String(e))
      ? "voicey unreachable from this origin (CORS or network) — the server lists the origins allowed to read its samples"
      : String(e.message || e).slice(0, 160);
    browserVoice(text || "Savante knows. Knowledge is what survives verification; nothing else counts.");
  }
  readout();
}

function browserVoice(text) {
  if (!("speechSynthesis" in window)) { S.tier = "silent — no voice tier on this browser"; readout(); return; }
  const u = new SpeechSynthesisUtterance(fitLine(text || "Savante knows."));
  u.rate = 0.98;
  u.onstart = () => { S.envelopeOn = true; S.envelope = 1; readout(); };
  u.onboundary = () => { S.envelope = 1; };   // a word boundary is all this tier reports
  u.onend = () => { S.envelopeOn = false; S.tier = "idle"; led("fc_led_voice", ""); readout(); };
  S.tier = "browser voice · envelope only (not measured)";
  S.backend = "speechSynthesis";
  led("fc_led_voice", "warn");
  speechSynthesis.speak(u);
}

// ── the senses ────────────────────────────────────────────────────────────────
async function eyeOn(on) {
  const sock = $("fc_cam").parentElement;
  if (!on) {
    if (S.cam) S.cam.getTracks().forEach((t) => t.stop());
    S.cam = null; $("fc_cam").srcObject = null; sock.classList.remove("live");
    readout(); return;
  }
  try {
    S.cam = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 480 } }, audio: false })
      .catch(() => navigator.mediaDevices.getUserMedia({ video: true, audio: false }));
    $("fc_cam").srcObject = S.cam;
    await $("fc_cam").play();
    sock.classList.add("live");
  } catch (e) {
    S.lastErr = `camera: ${String(e.name || e.message || e)}`;
    $("fc_eye").checked = false;
  }
  readout();
}

async function earOn(on) {
  if (!on) {
    if (S.mic) S.mic.getTracks().forEach((t) => t.stop());
    if (S.micSrc) { try { S.micSrc.disconnect(); } catch {} }
    S.mic = null; S.micSrc = null; S.micAn = null;
    $("fc_echo").checked = false;
    readout(); return;
  }
  try {
    ctx();
    S.mic = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true }, video: false });
    S.micSrc = S.actx.createMediaStreamSource(S.mic);
    S.micAn = S.actx.createAnalyser();
    S.micAn.fftSize = 2048;
    S.micAn.smoothingTimeConstant = 0.5;
    S.micSrc.connect(S.micAn);   // never to the destination: the ear listens, it does not play back
  } catch (e) {
    S.lastErr = `microphone: ${String(e.name || e.message || e)}`;
    $("fc_ear").checked = false;
  }
  readout();
}

// ── drawing ───────────────────────────────────────────────────────────────────
const buf = new Float32Array(2048);
function rms(an) {
  if (!an) return 0;
  an.getFloatTimeDomainData(buf);
  let s = 0;
  for (let i = 0; i < buf.length; i++) s += buf[i] * buf[i];
  return Math.sqrt(s / buf.length);
}

function drawMouth(cv, an, synthetic) {
  const c = cv.getContext("2d");
  const W = cv.width, H = cv.height, mid = H / 2, half = W / 2;
  c.clearRect(0, 0, W, H);
  // machine side: a CRT window with a graticule
  c.fillStyle = "rgba(3,8,6,.88)";
  c.beginPath(); c.roundRect(0, H * 0.12, half, H * 0.76, [H * 0.38, 0, 0, H * 0.38]); c.fill();
  c.strokeStyle = "rgba(125,255,178,.14)"; c.lineWidth = 1;
  for (let x = 0; x < half; x += W / 24) { c.beginPath(); c.moveTo(x, H * 0.12); c.lineTo(x, H * 0.88); c.stroke(); }
  c.beginPath(); c.moveTo(0, mid); c.lineTo(half, mid); c.stroke();

  let level = 0;
  const pts = [];
  if (an) {
    an.getFloatTimeDomainData(buf);
    let t0 = 0;
    for (let i = 1; i < buf.length / 2; i++) if (buf[i - 1] <= 0 && buf[i] > 0) { t0 = i; break; }
    const span = Math.min(buf.length - t0, 900);
    let s = 0;
    for (let i = 0; i < span; i++) { const v = buf[t0 + i]; s += v * v; pts.push(Math.max(-1, Math.min(1, v * 2.2))); }
    level = Math.sqrt(s / span);
  } else if (synthetic) {
    S.envelope *= 0.9;
    level = S.envelope * 0.25;
    const n = 240, ph = performance.now() / 90;
    for (let i = 0; i < n; i++) pts.push(Math.sin(i / 7 + ph) * S.envelope * 0.6 * Math.sin((Math.PI * i) / n));
  }
  // human side: the lips part with the level (a shadow under the photographed lips), never more than the level says
  const open = Math.min(1, level * 6);
  if (open > 0.02) {
    const g = c.createRadialGradient(half, mid, 1, half, mid, half * 0.9);
    g.addColorStop(0, `rgba(40,8,12,${0.75 * open})`); g.addColorStop(1, "rgba(40,8,12,0)");
    c.fillStyle = g;
    c.beginPath(); c.ellipse(half + half * 0.35, mid, half * 0.62, H * 0.32 * open + 1, 0, 0, Math.PI * 2); c.fill();
  }
  if (pts.length) {
    const n = pts.length;
    // the trace crosses the seam: phosphor green on the machine, lip-rose and soft on the skin
    for (const side of [0, 1]) {
      c.save();
      c.beginPath(); c.rect(side ? half : 0, 0, half, H); c.clip();
      c.strokeStyle = side ? "rgba(214,120,128,.55)" : "#7dffb2";
      c.shadowColor = side ? "rgba(214,120,128,.4)" : "#7dffb2";
      c.shadowBlur = side ? 3 : 8;
      c.lineWidth = side ? 2 : 1.6;
      c.beginPath();
      for (let i = 0; i < n; i++) {
        const x = (i / (n - 1)) * W;
        const taper = side ? Math.sin((Math.PI * i) / (n - 1)) : 1;   // the lips close at the corners
        const y = mid - pts[i] * (H * 0.36) * taper;
        i ? c.lineTo(x, y) : c.moveTo(x, y);
      }
      c.stroke();
      c.restore();
    }
  } else {
    c.strokeStyle = "rgba(125,255,178,.5)"; c.lineWidth = 1;
    c.beginPath(); c.moveTo(0, mid); c.lineTo(half, mid); c.stroke();
  }
  if (synthetic && !an) {
    c.fillStyle = "rgba(255,179,71,.85)"; c.font = `${Math.round(H / 7)}px ui-monospace,monospace`;
    c.fillText("envelope · not measured", 6, H * 0.3);
  }
  return level;
}

function drawEar(cv, an) {
  const c = cv.getContext("2d");
  const W = cv.width, cx = W / 2, cy = W / 2;
  c.clearRect(0, 0, W, W);
  const level = Math.min(1, rms(an) * 8);
  c.fillStyle = "#121826"; c.beginPath(); c.arc(cx, cy, W * 0.46, 0, Math.PI * 2); c.fill();
  c.strokeStyle = "#59657c"; c.lineWidth = 3; c.stroke();
  for (let k = 0; k < 4; k++) {
    const lit = an && level > k / 4;
    c.strokeStyle = lit ? `rgba(90,215,255,${0.45 + 0.5 * level})` : "rgba(90,215,255,.12)";
    c.lineWidth = 3;
    c.beginPath(); c.arc(cx, cy, W * (0.12 + k * 0.08), -Math.PI * 0.75, Math.PI * 0.75); c.stroke();
  }
  c.fillStyle = an ? `rgba(125,255,178,${0.4 + 0.6 * level})` : "#2a3344";
  c.beginPath(); c.arc(cx, cy, W * 0.06, 0, Math.PI * 2); c.fill();
  return level;
}

function frame() {
  S.raf = 0;
  if (!S.visible) return;
  const echo = $("fc_echo").checked && S.micAn;
  const speaking = S.tier.startsWith("voaicey · samples");
  const an = echo ? S.micAn : speaking ? S.speakAn : null;
  const level = drawMouth($("fc_mouth"), an, !an && S.envelopeOn);
  const ear = drawEar($("fc_earcv"), S.micAn);
  $("fc_glint").style.opacity = String(Math.min(0.9, level * 5));
  $("fc_iris").style.boxShadow = `0 0 ${10 + ear * 30}px rgba(90,215,255,.85), inset 0 0 10px rgba(90,215,255,.5)`;
  S.raf = requestAnimationFrame(frame);
}

// ── readout ───────────────────────────────────────────────────────────────────
function led(id, cls) { const e = $(id); if (e) e.className = "fc-led" + (cls ? " " + cls : ""); }

function readout() {
  const dl = $("fc_readout");
  if (!dl) return;
  const rows = [
    ["voice tier", S.tier],
    ["backend", S.backend],
    ["mouth source", $("fc_echo").checked && S.micAn ? "the ear (microphone)" : S.tier.includes("samples") ? "voaicey samples" : S.envelopeOn ? "envelope (not measured)" : "none — flat"],
    ["eye", S.cam ? "camera live · local only" : "closed"],
    ["ear", S.micAn ? "microphone live · local only" : "closed"],
    ["faceprint", "null — a render, not a measurement"],
    ["voiceprint", "null — nothing measured"],
  ];
  if (S.lastErr) rows.push(["last refusal", S.lastErr]);
  dl.replaceChildren();
  for (const [k, v] of rows) {
    const dt = document.createElement("dt"); dt.textContent = k;
    const dd = document.createElement("dd"); dd.textContent = v;
    dl.append(dt, dd);
  }
}

function fillVoices(voices, src) {
  const sel = $("fc_voice"), keep = sel.value;
  sel.replaceChildren();
  const own = document.createElement("option"); own.value = ""; own.textContent = "persona's own"; sel.append(own);
  for (const v of voices) { const o = document.createElement("option"); o.value = v; o.textContent = v; sel.append(o); }
  sel.value = voices.includes(keep) ? keep : "";
  sel.title = `voices from ${src}`;
}

// The presets the server honours. The known list is shown at once; the server's own answer replaces it if it comes
// within 8 s (an origin voicey does not allow gets no answer, so the known list stays, labelled as such).
async function loadVoices() {
  fillVoices(FALLBACK_VOICES, "the last list read from GET /voicey/voices (2026-11-25)");
  try {
    const u = new URL($("fc_url").value.trim());
    u.pathname = u.pathname.replace(/\/+$/, "") + "/voices";
    const ac = new AbortController();
    const t = setTimeout(() => ac.abort(), 8000);
    const r = await fetch(u.toString(), { mode: "cors", credentials: "omit", signal: ac.signal }).finally(() => clearTimeout(t));
    if (r.ok) {
      const d = await r.json();
      if (Array.isArray(d.voices) && d.voices.length) fillVoices(d.voices.map(String), `the server (${d.engine || "voicey"})`);
    }
  } catch {}
}

// ── room lifecycle ────────────────────────────────────────────────────────────
export function enter() {
  S.visible = true;
  readout();
  if (!S.raf) S.raf = requestAnimationFrame(frame);
}

export function leave() {
  S.visible = false;
  if (S.raf) cancelAnimationFrame(S.raf);
  S.raf = 0;
  stopSpeaking();
  if ($("fc_eye").checked) { $("fc_eye").checked = false; eyeOn(false); }
  if ($("fc_ear").checked) { $("fc_ear").checked = false; earOn(false); }
}

function init() {
  if (!$("fc_mouth")) return;
  const count = () => { $("fc_count").textContent = `${$("fc_text").value.length} / ${FREE_TEXT_MAX}`; };
  $("fc_text").addEventListener("input", count);
  $("fc_speak").addEventListener("click", () => speak($("fc_text").value));
  $("fc_oath").addEventListener("click", async () => {
    let oath = "I will render verdicts only from evidence I have read, and I will read before I rule.";
    try { oath = JSON.parse(await (await fetch("canon/savante.persona")).text()).oath || oath; } catch {}
    $("fc_text").value = fitLine(oath); count();
    speak($("fc_text").value);
  });
  $("fc_stop").addEventListener("click", stopSpeaking);
  $("fc_gain").addEventListener("input", (e) => { if (S.gain) S.gain.gain.value = +e.target.value; });
  $("fc_eye").addEventListener("change", (e) => eyeOn(e.target.checked));
  $("fc_ear").addEventListener("change", (e) => earOn(e.target.checked));
  $("fc_echo").addEventListener("change", (e) => {
    if (e.target.checked && !S.micAn) { $("fc_ear").checked = true; earOn(true); }
    readout();
  });
  $("fc_url").addEventListener("change", loadVoices);
  // the room is shown and hidden by app.js; follow its `hidden` attribute rather than couple the two modules
  const room = document.querySelector('[data-room="faicey"]');
  new MutationObserver(() => (room.hidden ? leave() : enter())).observe(room, { attributes: true, attributeFilter: ["hidden"] });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) { if (S.visible) leave(); } else if (!room.hidden) enter();
  });
  loadVoices();
  readout();
  drawMouth($("fc_mouth"), null, false);
  drawEar($("fc_earcv"), null);
  if (!room.hidden) enter();
}

if (typeof document !== "undefined") init();
