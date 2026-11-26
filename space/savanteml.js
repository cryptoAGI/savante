// SPDX-License-Identifier: MIT
// savanteML — Savante on browseML: the office running in the visitor's browser, on the visitor's CPU.
//
// browseML is bankML compiled to WebAssembly (browseml.js): it downloads a pinned model once, verifies every byte
// against its FORK.json before it answers, and puts bankML's receipt on every answer. savanteML is that engine shaped
// for Savante, and for the cluster:
//   answer()  Savante's own answer: her charter as the system prompt, a WHERE line bankML measured, the receipt checked
//   run()     a cluster job exactly as the host sent it (messages, max_tokens, temperature): no system line added, so
//             the host can re-run it and compare bytes; the receipt is checked here before it is sent anywhere
//   bench()   this browser's measured speeds (prompt and generation tokens a second), for the cluster's join and for an
//             honest projection of what it would contribute
// Nothing here talks to a network except the model download (Hugging Face, pinned revision). The model, the answers
// and the conversation stay in this browser.
import * as browseml from "./browseml.js";

export const MODEL = browseml.MODEL;
export const ENGINE = "browseml";                     // the dmind engine group's name prefix (bankml-q1: browseml/*)
export const PARAMS = 1_720_000_000;                  // Bonsai-1.7B: one generated token is 1.72 ITE (dmind.equivalence)
export const isReady = browseml.isReady, isBusy = browseml.isBusy, isLoading = browseml.isLoading;
export const isCached = browseml.isCached, threads = browseml.threads, abort = browseml.abort;

let verified = null;
/** What bankML verified at load: {model, sha256, version, threads, …}, or null. */
export const info = () => verified;

const sha256hex = async (t) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))]
  .map((b) => b.toString(16).padStart(2, "0")).join("");

/** Load (download once, then from the cache) and verify. progress(bytes, total, phase). */
export async function ensure(progress = () => {}) {
  if (browseml.isReady() && verified) return verified;
  verified = await browseml.load(progress, () => {});
  return verified;
}

async function chat(request, onPiece) {
  const t0 = performance.now();
  let text = "";
  const r = await browseml.chat(request, (p) => { text += p; onPiece && onPiece(p); }, () => {});
  const receipt = r.bankml_receipt || null;
  const ok = !!receipt && (await sha256hex(text)) === receipt.response_sha256 && (!verified || receipt.model_sha256 === verified.sha256);
  return { text, receipt, ok, usage: r.usage || {}, timings: r.timings || {}, seconds: (performance.now() - t0) / 1000,
           finish: r.choices?.[0]?.finish_reason || "stop" };
}

/** Savante's answer in this browser. history: [{role, content}], newest last. */
export async function answer({ system, history = [], message, maxTokens = 256, temperature }, onPiece) {
  const v = await ensure();
  const where = `WHERE YOU ARE RUNNING (measured by bankML just now): ${v.model} (sha256 ${v.sha256.slice(0, 16)}…), verified by ` +
    `bankML ${v.version}, in the visitor's own web browser, compiled to WebAssembly (savanteML on browseML), on ${v.threads} ` +
    `thread${v.threads > 1 ? "s" : ""} of their CPU — no server. Nothing of this conversation is sent anywhere or published.`;
  const messages = [{ role: "system", content: `${system}\n\n${where}` }, ...history.slice(-12), { role: "user", content: message }];
  return chat({ messages, max_tokens: maxTokens, ...(temperature == null ? {} : { temperature }) }, onPiece);
}

/** A cluster job, exactly as sent. A job with no temperature is greedy (dmind's jobs are: one right answer each). */
export async function run(job, onPiece) {
  await ensure();
  return chat({ messages: job.messages, max_tokens: job.max_tokens, temperature: job.temperature ?? 0 }, onPiece);
}

/** Measured speeds on a short fixed prompt: {prompt_tps, gen_tps, threads}. Loads the engine if it is cached. */
export async function bench() {
  const v = await ensure();
  const r = await chat({ messages: [{ role: "user", content: "Count from one to twenty in words, separated by commas." }],
                         max_tokens: 48, temperature: 0 });
  return { prompt_tps: Number(r.timings.prompt_per_second) || null, gen_tps: Number(r.timings.predicted_per_second) || null,
           threads: v.threads, ok: r.ok, tokens: (r.usage.prompt_tokens || 0) + (r.usage.completion_tokens || 0) };
}

/** ITE (dmind.equivalence) of a job's tokens through this model: (prompt + completion) × 1.72. */
export const ite = (promptTokens, completionTokens) => ((promptTokens || 0) + (completionTokens || 0)) * PARAMS / 1e9;
