import ZoneBadge from "./ZoneBadge";

const fmtTime = (iso) =>
  new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

function remaining(endIso, now) {
  const ms = new Date(endIso) - now;
  if (ms <= 0) return "leaving now";
  const mins = Math.round(ms / 60000);
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h === 0) return `${m}m left`;
  if (m === 0) return `${h}h left`;
  return `${h}h ${m}m left`;
}

function SessionCard({ session, now, mine, pending = false, canAct = false, onLeave, onExtend, busy }) {
  const left = remaining(session.end_time, now);
  const endingSoon = new Date(session.end_time) - now < 20 * 60000;
  const canExtend = session.duration_minutes + 30 <= 360;

  return (
    <article className={`card${mine ? " card-mine" : ""}${pending ? " card-pending" : ""}`}>
      <header className="card-head">
        <div className="card-title">
          <strong>{session.display_name}</strong>
          {pending ? <span className="tag-pending">Check your email</span> : mine && <span className="tag-you">You</span>}
        </div>
        <ZoneBadge zone={session.zone} level={session.level} />
      </header>

      <div className="card-time">
        <span>Here until <b>{fmtTime(session.end_time)}</b></span>
        <span className={`countdown${endingSoon ? " countdown-soon" : ""}`}>{left}</span>
      </div>

      {session.note && <p className="card-note">{session.note}</p>}
      {session.contact && (
        <div className="card-contact">
          <span className="muted">Contact</span> {session.contact}
        </div>
      )}

      {mine && !pending && canAct && (
        <div className="card-actions">
          <button type="button" className="btn-ghost" onClick={onExtend} disabled={busy || !canExtend}
            title={canExtend ? "Stay another 30 minutes" : "Posts can't run longer than 6 hours"}>
            +30 min
          </button>
          <button type="button" className="btn-ghost btn-ghost-danger" onClick={onLeave} disabled={busy}>
            I'm leaving
          </button>
        </div>
      )}
    </article>
  );
}

export default SessionCard;
