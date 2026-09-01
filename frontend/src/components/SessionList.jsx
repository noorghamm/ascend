import SessionCard from "./SessionCard";

function SessionList({ sessions }) {
  if (sessions.length === 0) {
    return <p>Nobody's posted yet. Be the first on the board.</p>;
  }

  return (
    <div>
      {sessions.map((s) => (
        <SessionCard key={s.id} session={s} />
      ))}
    </div>
  );
}

export default SessionList;