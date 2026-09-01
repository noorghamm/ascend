const ZONES = [
  { value: "all", label: "All zones" },
  { value: "group", label: "Green — group study (levels 2–3)" },
  { value: "quiet", label: "Amber — quiet study (levels 1, 4–7)" },
  { value: "silent", label: "Red — silent study (levels 8–12)" },
];

function ZoneFilter({ zone, onZoneChange }) {
  return (
    <select value={zone} onChange={(e) => onZoneChange(e.target.value)}>
      {ZONES.map((z) => (
        <option key={z.value} value={z.value}>
          {z.label}
        </option>
      ))}
    </select>
  );
}

export default ZoneFilter;