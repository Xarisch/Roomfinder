const API = "http://localhost:8000";

// ── State ──────────────────────────────────────────────
const state = {
  days: 0,
  free: true,       // true = nur freie, false = alle
  view: "all",      // "all" | "building" | "room"
};

// ── DOM refs ───────────────────────────────────────────
const statusDot      = document.getElementById("status-dot");
const statusText     = document.getElementById("status-text");
const buildingsCont  = document.getElementById("buildings-container");
const roomResult     = document.getElementById("room-result");
const currentDate    = document.getElementById("current-date");

const buildingSection = document.getElementById("building-search-section");
const roomSection     = document.getElementById("room-search-section");
const buildingInput   = document.getElementById("building-input");
const roomInput       = document.getElementById("room-input");

// ── Date display ───────────────────────────────────────
function formatDate(daysOffset) {
  const d = new Date();
  d.setDate(d.getDate() + daysOffset);
  return d.toLocaleDateString("de-DE", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" });
}

currentDate.textContent = formatDate(0);

// ── Status helpers ─────────────────────────────────────
function setStatus(type, msg) {
  statusDot.className = "dot " + type;
  statusText.textContent = msg;
}

// ── Button group logic ─────────────────────────────────
function activateBtn(groupId, matchFn) {
  document.getElementById(groupId).querySelectorAll("button").forEach(btn => {
    btn.classList.toggle("active", matchFn(btn));
  });
}

document.getElementById("day-selector").addEventListener("click", e => {
  if (e.target.tagName !== "BUTTON") return;
  state.days = parseInt(e.target.dataset.days);
  currentDate.textContent = formatDate(state.days);
  activateBtn("day-selector", b => parseInt(b.dataset.days) === state.days);
  refresh();
});

document.getElementById("filter-selector").addEventListener("click", e => {
  if (e.target.tagName !== "BUTTON") return;
  state.free = e.target.dataset.free === "true";
  activateBtn("filter-selector", b => b.dataset.free === String(state.free));
  refresh();
});

document.getElementById("view-selector").addEventListener("click", e => {
  if (e.target.tagName !== "BUTTON") return;
  state.view = e.target.dataset.view;
  activateBtn("view-selector", b => b.dataset.view === state.view);
  updateViewSections();
  refresh();
});

function updateViewSections() {
  buildingSection.style.display = state.view === "building" ? "flex" : "none";
  roomSection.style.display     = state.view === "room"     ? "flex" : "none";
  roomResult.innerHTML          = "";
}

// ── API calls ──────────────────────────────────────────
async function fetchAllRooms() {
  const res = await fetch(`${API}/find/all-rooms?days=${state.days}&free=${state.free}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function fetchBuilding(name) {
  const res = await fetch(`${API}/find/rooms-b?building=${encodeURIComponent(name)}&days=${state.days}&free=${state.free}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function fetchRoom(name) {
  const res = await fetch(`${API}/find/room?room=${encodeURIComponent(name)}&days=${state.days}&free=${state.free}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Render helpers ─────────────────────────────────────

// Groups a flat list of {building, room} into { buildingName: [room, ...] }
function groupByBuilding(flatList) {
  const map = {};
  for (const item of flatList) {
    const key = item.building || "Unbekannt";
    if (!map[key]) map[key] = [];
    map[key].push(item.room ?? item);
  }
  return map;
}

function roomRow(room) {
  const occupied = room.Besetzt;
  const div = document.createElement("div");
  div.className = "room";

  const nameEl = document.createElement("span");
  nameEl.className = "room-name";
  nameEl.textContent = room.Raum || "–";

  const middleEl = document.createElement("span");
  middleEl.className = "room-event";
  if (occupied && room.event) middleEl.textContent = room.event;

  const rightEl = document.createElement("span");
  rightEl.className = "room-time";
  if (occupied && room.time) rightEl.textContent = room.time;

  const badge = document.createElement("span");
  badge.className = "badge " + (occupied ? "occupied" : "free");
  badge.textContent = occupied ? "belegt" : "frei";

  div.appendChild(nameEl);
  div.appendChild(middleEl);
  div.appendChild(rightEl);
  div.appendChild(badge);
  return div;
}

function buildingBlock(name, rooms) {
  const freeCount = rooms.filter(r => !r.Besetzt).length;
  const occCount  = rooms.filter(r =>  r.Besetzt).length;

  const wrap = document.createElement("div");
  wrap.className = "building";

  const header = document.createElement("div");
  header.className = "building-header";
  header.innerHTML = `
    <span class="bname">${name}</span>
    <span class="bstats">
      <span class="fc">▲ ${freeCount} frei</span>
      <span class="oc">▼ ${occCount} belegt</span>
    </span>
    <span class="chevron">▼</span>
  `;

  const roomsCont = document.createElement("div");
  roomsCont.className = "rooms";
  rooms.forEach(r => roomsCont.appendChild(roomRow(r)));

  header.addEventListener("click", () => wrap.classList.toggle("open"));
  wrap.appendChild(header);
  wrap.appendChild(roomsCont);
  return wrap;
}

function renderBuildings(grouped) {
  buildingsCont.innerHTML = "";
  const keys = Object.keys(grouped);
  if (!keys.length) {
    buildingsCont.innerHTML = '<p class="empty">Keine Räume gefunden.</p>';
    return;
  }
  const container = document.createElement("div");
  container.className = "buildings";
  keys.forEach(k => container.appendChild(buildingBlock(k, grouped[k])));
  buildingsCont.appendChild(container);
}

function renderRoomCard(data) {
  roomResult.innerHTML = "";
  if (typeof data === "string") {
    roomResult.innerHTML = `<p class="empty">${data}</p>`;
    return;
  }
  const card = document.createElement("div");
  card.className = "room-card";
  const occupied = data.details?.Besetzt;
  card.innerHTML = `
    <span class="rc-name">${data.details?.Raum ?? "–"}</span>
    <span class="rc-building">${data.building ?? ""}</span>
    <span class="rc-info">${data.details?.Zusatzinfo ?? ""}</span>
    <span class="rc-status ${occupied ? "occupied" : "free"}">
      ${occupied ? `● Belegt · ${data.details.time} · ${data.details.event}` : "● Frei"}
    </span>
  `;
  roomResult.appendChild(card);
}

// ── Main refresh ───────────────────────────────────────
async function refresh() {
  buildingsCont.innerHTML = "";
  roomResult.innerHTML    = "";

  if (state.view === "room") return; // room search is manual

  setStatus("loading", "Lade Daten…");

  try {
    if (state.view === "all") {
      const data = await fetchAllRooms();
      // all-rooms returns [{building, room}, ...]
      const grouped = groupByBuilding(data);
      renderBuildings(grouped);
      const total = data.length;
      setStatus("ok", `${total} Räume geladen`);

    } else if (state.view === "building") {
      const name = buildingInput.value.trim();
      if (!name) { setStatus("ok", "Gebäude eingeben"); return; }
      const data = await fetchBuilding(name);
      if (!Array.isArray(data) || !data.length) {
        buildingsCont.innerHTML = '<p class="empty">Keine Räume gefunden.</p>';
        setStatus("ok", "Keine Ergebnisse");
        return;
      }
      // rooms-b returns an array of room objects directly
      const grouped = { [name]: data };
      renderBuildings(grouped);
      setStatus("ok", `${data.length} Räume in ${name}`);
    }

  } catch (err) {
    setStatus("err", "Fehler: " + err.message);
    buildingsCont.innerHTML = '<p class="empty">API nicht erreichbar.</p>';
  }
}

// ── Search button handlers ─────────────────────────────
document.getElementById("building-search-btn").addEventListener("click", refresh);
buildingInput.addEventListener("keydown", e => { if (e.key === "Enter") refresh(); });

document.getElementById("room-search-btn").addEventListener("click", async () => {
  const name = roomInput.value.trim();
  if (!name) return;
  setStatus("loading", "Suche Raum…");
  try {
    const data = await fetchRoom(name);
    renderRoomCard(data);
    setStatus("ok", "Raum gefunden");
  } catch (err) {
    setStatus("err", "Fehler: " + err.message);
  }
});

roomInput.addEventListener("keydown", e => {
  if (e.key === "Enter") document.getElementById("room-search-btn").click();
});

// ── Note about router params ───────────────────────────
// The router endpoints need to accept days + free as query params.
// Update router.py:
//
// @router.get("/all-rooms")
// def get_all_rooms(days: int = 0, free: bool = True):
//     return RoomFilter(days_forwarded=days, search_free=free).get_all_free_rooms()
//
// @router.get("/rooms-b")
// def get_rooms_by_buildings(building: str, days: int = 0, free: bool = True):
//     return RoomFilter(days_forwarded=days, search_free=free).get_rooms_in_building(building)
//
// @router.get("/room")
// def get_room_by_name(room: str, days: int = 0, free: bool = True):
//     return RoomFilter(days_forwarded=days, search_free=free).search_room(room)

// ── Init ───────────────────────────────────────────────
refresh();