export const ZONES = [
  { value: "group", label: "Green", title: "Group study", colour: "green", levels: [2, 3] },
  { value: "quiet", label: "Amber", title: "Quiet study", colour: "amber", levels: [1, 4, 5, 6, 7] },
  { value: "silent", label: "Red", title: "Silent study", colour: "red", levels: [8, 9, 10, 11, 12] },
];

export const ZONE_BY_KEY = Object.fromEntries(ZONES.map((z) => [z.value, z]));

export function levelsLabel(zone) {
  const l = zone.levels;
  if (zone.value === "quiet") return "levels 1, 4–7";
  return `levels ${l[0]}–${l[l.length - 1]}`;
}
