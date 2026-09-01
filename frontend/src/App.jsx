import { useState, useEffect } from "react";
import SessionList from "./components/SessionList";
import ZoneFilter from "./components/ZoneFilter";
const API = "http://127.0.0.1:8000/api";

function App() {
  const [sessions, setSessions] = useState([]);
  const [zone, setZone] = useState("all");

  useEffect(() => {
    fetch(`${API}/sessions/`)
      .then((res) => res.json())
      .then((data) => setSessions(data));
  }, []);

  const visibleSessions =
    zone === "all" ? sessions : sessions.filter((s) => s.zone === zone);

  return (
    <div>
      <h1>Ascend</h1>
      <p>Find your level.</p>
      <ZoneFilter zone={zone} onZoneChange={setZone} />
      <SessionList sessions={visibleSessions} />
    </div>
  );
}

export default App;