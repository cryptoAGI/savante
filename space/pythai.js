// pythai.js — the PYTHAI room: huggingface.co/PYTHAI read from the visitor's browser, and whether every public copy
// of the office carries canon main. Public GETs only; there is no write path, signed in or not. Shared by both
// editions of the page (space/ and space/interactive/), so the room is written once. Every string from the Hub or
// GitHub is written with textContent.
import { hubReading, orgReading, driftReading, ORG } from "./savante.js";

const $ = (id) => document.getElementById(id);
let ORG_ROWS = [], ORG_SORT = { k: "kind", dir: 1 };
function td(text, cls) { const c = document.createElement("td"); c.textContent = text ?? "—"; if (cls) c.className = cls; return c; }
function drawOrg() {
  const q = $("pyfilter").value.trim().toLowerCase();
  const rows = ORG_ROWS.filter((r) => !q || JSON.stringify(r).toLowerCase().includes(q));
  const { k, dir } = ORG_SORT;
  rows.sort((a, b) => {
    const x = a[k] ?? "", y = b[k] ?? "";
    return (typeof x === "number" && typeof y === "number" ? x - y : String(x).localeCompare(String(y))) * dir;
  });
  const tb = $("pyrows");
  tb.replaceChildren();
  for (const r of rows) {
    const tr = document.createElement("tr");
    const idc = document.createElement("td");
    const a = document.createElement("a"); a.href = r.url; a.target = "_blank"; a.rel = "noopener"; a.textContent = r.id;
    idc.append(a);
    tr.append(td(r.kind), idc, td(r.what), td(r.license), td((r.last_modified || "").slice(0, 10)), td(r.downloads), td(r.likes));
    if (r.kind === "model") {
      tr.classList.add("pick");
      tr.title = "take a Hub reading";
      tr.addEventListener("click", async (e) => {
        if (e.target.tagName === "A") return;
        $("pyout").textContent = "reading…";
        $("pyout").textContent = JSON.stringify(await hubReading(r.id), null, 1);
      });
    }
    tb.append(tr);
  }
}
async function readOrg() {
  $("pynote").textContent = `reading huggingface.co/${ORG}…`;
  const o = await orgReading(ORG);
  ORG_ROWS = o.rows || [];
  $("pynote").textContent = o.refused ? o.refused
    : `${o.count.model} models · ${o.count.dataset} datasets · ${o.count.space} Spaces · read ${o.read_at_utc}` +
      (o.errors.length ? ` · not read: ${o.errors.map((e) => e.kind + " " + (e.status || e.error)).join(", ")}` : "") +
      ` — ${o.standing}`;
  drawOrg();
}
async function readDrift() {
  const tb = $("pydriftrows");
  const wait = document.createElement("tr");
  wait.append(td("reading GitHub and the Hub…"));
  tb.replaceChildren(wait);
  const d = await driftReading();
  tb.replaceChildren();
  for (const r of d.rows) {
    const tr = document.createElement("tr");
    tr.append(td(r.surface), td(r.kind), td((r.carries || "").slice(0, 7) || "—"),
              td(r.state, r.state === "AGREES" ? "ok" : r.state === "unreadable" ? "warn" : "bad"), td(r.note));
    tb.append(tr);
  }
  const c = d.canon;
  $("pydriftnote").textContent = (c ? `canon main is ${c.commit.slice(0, 7)} (${c.date}) — ${c.subject}`
    : `canon main unreadable: ${d.canon_error}`) + ` · read ${d.read_at_utc} — ${d.standing}`;
}
if ($("pyrows")) {   // only on a page that has the room
  $("pygo").addEventListener("click", readOrg);
  $("pydrift").addEventListener("click", readDrift);
  $("pyfilter").addEventListener("input", drawOrg);
  document.querySelectorAll("table.sortable th[data-k]").forEach((th) => th.addEventListener("click", () => {
    ORG_SORT = { k: th.dataset.k, dir: ORG_SORT.k === th.dataset.k ? -ORG_SORT.dir : 1 };
    drawOrg();
  }));
  // The first time the room is shown, however it is reached (its button, #pythai, the hash changing), read it once.
  let pyRead = false;
  const pyRoom = document.querySelector('[data-room="pythai"]');
  const pyFirst = () => { if (pyRead || pyRoom.hidden) return; pyRead = true; readOrg().then(readDrift); };
  new MutationObserver(pyFirst).observe(pyRoom, { attributes: true, attributeFilter: ["hidden"] });
  pyFirst();
}
