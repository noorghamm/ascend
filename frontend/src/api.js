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
