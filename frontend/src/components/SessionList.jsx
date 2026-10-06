import SessionCard from "./SessionCard";
import { ZONES, levelsLabel } from "../zones";

function SessionList({ sessions, zone, now, mine, pending }) {
  if (sessions.length === 0 && !pending) {
    return (
      <div className="empty">
        <p>Nobody's on the board right now.</p>
        <p className="muted">Post when you're in and let people find you.</p>
      </div>
    );
  }

  const groups = ZONES.filter((z) => zone === "all" || z.value === zone).map((z) => ({
    zone: z,
    items: sessions.filter((s) => s.zone === z.value),
    pending: pending && pending.zone === z.value ? pending : null,
  }));

  return (
    <div className="groups">
      {groups.map(({ zone: z, items, pending: p }) => (
        <section key={z.value} className="group" id={`zone-${z.value}`}>
          <h2 className="group-head">
            <span className={`dot dot-${z.colour}`} />
            {z.title}
            <span className="muted group-meta">
              {levelsLabel(z)} · {items.length}
            </span>
          </h2>
          {items.length === 0 && !p ? (
            <p className="muted group-empty">No one here yet.</p>
          ) : (
            <div className="cards">
              {p && <SessionCard key="pending" session={p} now={now} pending />}
              {items.map((s) => (
                <SessionCard key={s.id} session={s} now={now} mine={mine.has(s.id)} />
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  );
}

export default SessionList;
