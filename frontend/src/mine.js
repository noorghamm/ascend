// Posts that belong to this browser: id -> owner_key. The key lets the API
// trust "I'm leaving" and "+30 min" from the UI without the email link.
const KEY = "ascend:mine";

function read() {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) ?? "{}");
    if (Array.isArray(raw)) return Object.fromEntries(raw.map((id) => [id, null]));
    return raw && typeof raw === "object" ? raw : {};
  } catch {
    return {};
  }
}

function write(obj) {
  try {
    localStorage.setItem(KEY, JSON.stringify(obj));
  } catch {
    /* private mode etc. */
  }
  return obj;
}

export function loadMine() {
  return read();
}

export function addMine(id, ownerKey = null) {
  const m = read();
  m[Number(id)] = ownerKey ?? m[Number(id)] ?? null;
  return write(m);
}

export function removeMine(id) {
  const m = read();
  delete m[Number(id)];
  return write(m);
}

export const isMine = (mine, id) => Object.prototype.hasOwnProperty.call(mine, id);
export const keyFor = (mine, id) => mine[id] ?? null;
