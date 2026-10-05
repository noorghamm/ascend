// Remember which posts belong to this browser so the board can tag them "You".
const KEY = "ascend:mine";

export function loadMine() {
  try {
    return new Set(JSON.parse(localStorage.getItem(KEY) ?? "[]"));
  } catch {
    return new Set();
  }
}

export function addMine(id) {
  const set = loadMine();
  set.add(Number(id));
  try {
    localStorage.setItem(KEY, JSON.stringify([...set]));
  } catch {
    /* private mode etc. */
  }
  return set;
}
