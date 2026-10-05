import { ZONE_BY_KEY } from "../zones";

function ZoneBadge({ zone, level, size = "sm" }) {
  const z = ZONE_BY_KEY[zone];
  if (!z) return null;
  return (
    <span className={`pill pill-${z.colour} pill-${size}`}>
      <span className="pill-dot" />
      {z.label}
      {level ? <span className="pill-level">L{level}</span> : null}
    </span>
  );
}

export default ZoneBadge;
