// Small per-browser conveniences.
const FORM = "ascend:form";
const HOWTO = "ascend:howto-dismissed";

export function loadFormPrefs() {
  try {
    const p = JSON.parse(localStorage.getItem(FORM) ?? "{}");
    return { email: p.email ?? "", display_name: p.display_name ?? "" };
  } catch {
    return { email: "", display_name: "" };
  }
}

export function saveFormPrefs({ email, display_name }) {
  try {
    localStorage.setItem(FORM, JSON.stringify({ email, display_name }));
  } catch {
    /* ignore */
  }
}

export function howtoDismissed() {
  try {
    return localStorage.getItem(HOWTO) === "1";
  } catch {
    return false;
  }
}

export function dismissHowto() {
  try {
    localStorage.setItem(HOWTO, "1");
  } catch {
    /* ignore */
  }
}
