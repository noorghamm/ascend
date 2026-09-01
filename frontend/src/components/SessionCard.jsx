function SessionCard({ session }) {
  const hours = session.duration_minutes / 60;

  return (
    <div className="session-card">
      <strong>{session.display_name}</strong> — {session.zone}
      {session.level && ` (level ${session.level})`}
      <div>
        {new Date(session.start_time).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })}{" "}
        · {hours} {hours === 1 ? "hour" : "hours"}
      </div>
      {session.note && <div>{session.note}</div>}
      {session.contact && <div>Contact: {session.contact}</div>}
    </div>
  );
}

export default SessionCard;