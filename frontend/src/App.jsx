import { useCallback, useEffect, useMemo, useState } from "react";
import SessionList from "./components/SessionList";
import ZoneFilter from "./components/ZoneFilter";
import SessionForm from "./components/SessionForm";
import Toast from "./components/Toast";
import { fetchSessions } from "./api";
import { addMine, loadMine } from "./mine";

const POLL_MS = 30_000;

function readFlash() {
  const q = new URLSearchParams(window.location.search);
  let toast = null;
  let verifiedId = null;
  if (q.has("verified")) {
    verifiedId = Number(q.get("verified"));
    toast = { kind: "ok", text: "You're live on the board." };
  } else if (q.has("removed")) {
    toast = { kind: "ok", text: "Your post has been removed." };
  } else if (q.has("expired")) {
    toast = { kind: "err", text: "That post has already ended. Post again if you're still in." };
  }
  if (toast) window.history.replaceState({}, "", window.location.pathname);
  return { toast, verifiedId };
}

function App() {
  const [sessions, setSessions] = useState([]);
  const [loadError, setLoadError] = useState(null);
  const [zone, setZone] = useState("all");
  const [now, setNow] = useState(() => new Date());
  // Flash messages from verify/remove redirects are read once, on first render.
  const [flash] = useState(readFlash);
  const [mine, setMine] = useState(() =>
    flash.verifiedId ? addMine(flash.verifiedId) : loadMine()
  );
  const [toast, setToast] = useState(flash.toast);
  const [formOpen, setFormOpen] = useState(false);

  const loadSessions = useCallback(() =>
    fetchSessions()
      .then((data) => {
        setSessions(data);
        setLoadError(null);
        setNow(new Date());
      })
      .catch((e) => setLoadError(e.message)),
  []);

  // Load, then poll. Also tick the clock every minute so countdowns stay honest.
  useEffect(() => {
    loadSessions();
    const poll = setInterval(loadSessions, POLL_MS);
    const tick = setInterval(() => setNow(new Date()), 60_000);
    return () => {
      clearInterval(poll);
      clearInterval(tick);
    };
  }, [loadSessions]);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 6000);
    return () => clearTimeout(t);
  }, [toast]);

  const live = useMemo(() => sessions.filter((s) => new Date(s.end_time) > now), [sessions, now]);

  const counts = useMemo(() => {
    const c = { all: live.length };
    for (const s of live) c[s.zone] = (c[s.zone] ?? 0) + 1;
    return c;
  }, [live]);

  // Own posts first within each zone; otherwise API order (newest first).
  const ordered = useMemo(
    () => [...live].sort((a, b) => Number(mine.has(b.id)) - Number(mine.has(a.id))),
    [live, mine]
  );

  const handleCreated = (created) => {
    // Remember the post now so it's tagged "You" the moment it goes live.
    if (created?.id) setMine(addMine(created.id));
    setToast({ kind: "ok", text: "Posted. Check your email to go live." });
    setFormOpen(false);
  };

  return (
    <div className="app">
      <Toast toast={toast} onClose={() => setToast(null)} />

      <header className="top">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <div>
            <h1>Ascend</h1>
            <p className="tagline">Find your level. University of Glasgow Library.</p>
          </div>
        </div>
        <div className="top-meta">
          <span className="live-dot" /> {live.length} on the board
          <button type="button" className="btn btn-sm post-toggle" onClick={() => setFormOpen((o) => !o)}>
            {formOpen ? "Close" : "+ Post"}
          </button>
        </div>
      </header>

      <main className="layout">
        <aside className={`side${formOpen ? " side-open" : ""}`}>
          <div className="panel">
            <h2 className="panel-title">I'm in the library</h2>
            <SessionForm onCreated={handleCreated} />
          </div>
        </aside>

        <section className="board">
          <div className="board-bar">
            <ZoneFilter zone={zone} onZoneChange={setZone} counts={counts} />
            <button type="button" className="link" onClick={loadSessions}>Refresh</button>
          </div>
          {loadError && (
            <div className="notice notice-err">
              Can't reach the API ({loadError}). Is the backend running?
            </div>
          )}
          <SessionList sessions={ordered} zone={zone} now={now} mine={mine} />
        </section>
      </main>

      <footer className="foot muted">
        Posts expire automatically. Nothing is stored beyond your name, zone and note.
      </footer>
    </div>
  );
}

export default App;
