export const API = import.meta.env.VITE_API_URL ?? "/api";

export async function fetchSessions() {
  const res = await fetch(`${API}/sessions/`);
  if (!res.ok) throw new Error(`Board failed to load (${res.status})`);
  return res.json();
}

export async function createSession(body) {
  const res = await fetch(`${API}/sessions/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, data };
}

async function ownerAction(id, action, ownerKey) {
  const res = await fetch(`${API}/sessions/${id}/${action}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ owner_key: ownerKey }),
  });
  if (res.status === 204) return { ok: true, data: null };
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, data };
}

export const leaveSession = (id, key) => ownerAction(id, "leave", key);
export const extendSession = (id, key) => ownerAction(id, "extend", key);
