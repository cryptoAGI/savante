// SPDX-License-Identifier: MIT
// The rooms as tabs inside the ultimate input field (uif-space.js), shared by both editions of the page.
//
// The field floats over every room, so its button row is the one place a visitor can always reach: each room is a
// button there (a tab), and a T-mode command of the same name (`faicey`, `pythai`, … and `room <name>`). The page's
// own <nav> stays in the markup as the fallback, and is hidden only once the field has mounted: without the bundle,
// or before it loads, the header tabs work as they always did.
//
// Nothing here talks to a model, the network or storage beyond the field's own saved button rows (see resetBars).

/** The rooms, read from the page's own nav, so the field and the header can never disagree. */
export function rooms() {
  return [...document.querySelectorAll("nav button[data-go]")].map((b) => ({ id: b.dataset.go, label: b.textContent.trim() }));
}

const ICON = { ask: "✎", about: "ⓘ", faicey: "◑", pythai: "⧉", hub: "⌕", office: "🏛", verdict: "⚖", integrity: "✓", skills: "📜", settings: "⚙" };
export const tabId = (room) => `sv-room-${room}`;

/**
 * One action per room. `extra[room]` may add to a tab: `{ description, run(ctx) }` runs after the room opens (for
 * example Integrity re-hashes, Hub takes `hub <owner/name>`); return true from it to stay where you are instead.
 */
export function roomActions(goRoom, extra = {}) {
  const list = rooms();
  const tabs = list.map(({ id, label }) => ({
    id: tabId(id), label, command: id, icon: ICON[id] || "▢",
    description: extra[id]?.description || `${id} - open the ${label} room`,
    async run(ctx) {
      if (extra[id]?.before && (await extra[id].before(ctx))) return;
      goRoom(id);
      if (extra[id]?.run) await extra[id].run(ctx);
    },
  }));
  tabs.push({
    id: "sv-rooms", label: "Rooms", command: "room", aliases: ["rooms", "tab", "go"], icon: "☰", defaultHidden: true,
    description: `room [${list.map((r) => r.id).join("|")}] - open a room (no name: list them)`,
    run(ctx) {
      const want = (ctx.args[0] || "").toLowerCase();
      const hit = list.find((r) => r.id === want || r.label.toLowerCase() === want);
      if (!hit) { list.forEach((r) => ctx.print(`  ${r.id.padEnd(10)} ${r.label}`)); return; }
      goRoom(hit.id);
      ctx.print(`room: ${hit.label}`);
    },
  });
  return tabs;
}

/** The tab ids, in nav order, for a mode's button row. */
export const tabIds = () => rooms().map((r) => tabId(r.id));

/**
 * The field saves each mode's button row per visitor. A row saved before the tabs existed would hide them, so once
 * per `version` the saved rows (and only the rows: .history, .memory and the outputs are kept) are cleared and the
 * mode's standard row, tabs first, is laid out again.
 */
export function resetBars(storageKey, version) {
  try {
    const flag = `savante.uif.bars:${storageKey}`;
    if (localStorage.getItem(flag) === version) return;
    for (const m of ["chat", "persona", "terminal"]) localStorage.removeItem(`uif:${storageKey}:bar:${m}`);
    localStorage.setItem(flag, version);
  } catch { /* storage blocked: the field starts from the standard rows anyway */ }
}

/**
 * Mark the open room's tab. The field draws its buttons itself (React) and names each one in its title as
 * "label  (command)"; a rule keyed on the root's data attribute styles the open one, so a re-render cannot lose it.
 */
export function markTabs() {
  const css = rooms().map(({ id }) =>
    `:root[data-open-room="${id}"] #uif-root .uif-action[title*="  (${id})"]` +
    "{color:var(--amber,#e0a040);border-color:var(--amber,#e0a040);box-shadow:inset 0 -2px 0 var(--amber,#e0a040)}").join("\n");
  const style = document.createElement("style");
  style.id = "uiftabs-active";
  style.textContent = css;
  document.head.append(style);
}

/** Call from showRoom: the open room, for markTabs. */
export const setActive = (room) => { document.documentElement.dataset.openRoom = room; };

/** The field mounted: its row now holds the tabs, so the header's copy steps aside. */
export function fieldHoldsTabs() {
  document.body.classList.add("uif-tabs");
  markTabs();
}

// ── a stream over the page's carriers, which write into elements ────────────────────────────────────────────────
// The carriers set out.textContent to the answer so far and meta.textContent to how it is being delivered. `sink`
// turns those writes into the new text only, and `streamOf` makes the async generator the field's `ask` returns.
export function streamOf(run) {
  const q = []; let wake = null, end = false, err = null;
  const poke = () => { const w = wake; wake = null; w && w(); };
  run((x) => { q.push(x); poke(); }).then(() => { end = true; poke(); }, (e) => { err = e; end = true; poke(); });
  return (async function* () {
    for (;;) {
      while (q.length) yield q.shift();
      if (end) { if (err) throw err; return; }
      await new Promise((r) => { wake = r; });
    }
  })();
}
export function sink(push) {
  let shown = "";
  return {
    get textContent() { return shown; },
    set textContent(t) {
      t = String(t);
      if (t.startsWith(shown)) { if (t.length > shown.length) push(t.slice(shown.length)); shown = t; }
      else if (!shown.startsWith(t.trim())) { push("\n\n" + t); shown += "\n\n" + t; }  // a replacement (an error, a refusal) is shown, not hidden
    },
  };
}
