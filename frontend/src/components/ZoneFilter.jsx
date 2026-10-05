import { ZONES } from "../zones";

function ZoneFilter({ zone, onZoneChange, counts }) {
  const chips = [{ value: "all", label: "All", colour: null }, ...ZONES];
  return (
    <div className="chips" role="tablist" aria-label="Filter by zone">
      {chips.map((z) => (
        <button
          key={z.value}
          type="button"
          role="tab"
          aria-selected={zone === z.value}
          className={`chip${zone === z.value ? " chip-on" : ""}`}
          onClick={() => onZoneChange(z.value)}
        >
          {z.colour && <span className={`dot dot-${z.colour}`} />}
          {z.label}
          <span className="chip-count">{counts[z.value] ?? 0}</span>
        </button>
      ))}
    </div>
  );
}

export default ZoneFilter;
