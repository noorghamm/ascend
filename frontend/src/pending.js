// A post you've submitted but not yet verified. Local to this browser only.
const KEY = "ascend:pending";

export function loadPending() {
  try {
    const p = JSON.parse(localStorage.getItem(KEY) ?? "null");
    if (p && new Date(p.end_time) > new Date()) return p;
  } catch {
    /* ignore */
  }
  return null;
}

export function savePending(session) {
  try {
    localStorage.setItem(KEY, JSON.stringify(session));
  } catch {
    /* ignore */
  }
  return session;
}

export function clearPending() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
  return null;
}
