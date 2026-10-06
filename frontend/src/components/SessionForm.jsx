import { useState } from "react";
import { createSession } from "../api";
import { ZONES, ZONE_BY_KEY, levelsLabel } from "../zones";
import { loadFormPrefs, saveFormPrefs } from "../prefs";

const DURATIONS = [30, 60, 90, 120, 150, 180, 240, 300, 360];
const fmtDuration = (m) => (m < 60 ? `${m} min` : m % 60 ? `${m / 60} h` : `${m / 60} h`);

const EMPTY = {
  email: "",
  display_name: "",
  zone: "group",
  level: "",
  duration_minutes: 60,
  note: "",
  contact: "",
};

function SessionForm({ onCreated }) {
  const [form, setForm] = useState(() => ({ ...EMPTY, ...loadFormPrefs() }));
  const [status, setStatus] = useState("idle"); // idle | sending | sent
  const [errors, setErrors] = useState({});

  const set = (name, value) => setForm((f) => ({ ...f, [name]: value }));

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "zone") {
      // Level choices depend on zone; reset if the old level isn't valid.
      const ok = ZONE_BY_KEY[value].levels.includes(Number(form.level));
      setForm((f) => ({ ...f, zone: value, level: ok ? f.level : "" }));
    } else {
      set(name, value);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("sending");
    const body = {
      ...form,
      level: form.level === "" ? null : Number(form.level),
      duration_minutes: Number(form.duration_minutes),
      start_time: new Date().toISOString(),
    };
    const { ok, data } = await createSession(body);
    if (ok) {
      saveFormPrefs(form);
      onCreated(data);
      setErrors({});
      setForm({ ...EMPTY, email: form.email, display_name: form.display_name });
      setStatus("sent");
    } else {
      setErrors(data);
      setStatus("idle");
    }
  };

  const zone = ZONE_BY_KEY[form.zone];
  const err = (k) => errors[k] && <p className="error">{Array.isArray(errors[k]) ? errors[k][0] : errors[k]}</p>;

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      {status === "sent" && (
        <div className="notice notice-ok">
          <b>Check your email.</b> Click the link to put your post on the board.
        </div>
      )}
      {errors.non_field_errors && <div className="notice notice-err">{errors.non_field_errors[0]}</div>}

      <label className="field">
        <span>Student email</span>
        <input
          name="email"
          type="email"
          autoComplete="email"
          value={form.email}
          onChange={handleChange}
          placeholder="1234567a@student.gla.ac.uk"
          required
        />
        {err("email")}
      </label>

      <label className="field">
        <span>Name shown on the board</span>
        <input
          name="display_name"
          value={form.display_name}
          onChange={handleChange}
          placeholder="Noor"
          maxLength={50}
          required
        />
        {err("display_name")}
      </label>

      <fieldset className="field">
        <legend>Zone</legend>
        <div className="seg">
          {ZONES.map((z) => (
            <label key={z.value} className={`seg-opt seg-${z.colour}${form.zone === z.value ? " seg-on" : ""}`}>
              <input
                type="radio"
                name="zone"
                value={z.value}
                checked={form.zone === z.value}
                onChange={handleChange}
              />
              <span className={`dot dot-${z.colour}`} />
              {z.label}
            </label>
          ))}
        </div>
        <p className="hint">{zone.title} · {levelsLabel(zone)}</p>
        {err("zone")}
      </fieldset>

      <div className="row">
        <label className="field">
          <span>Level <span className="muted">(optional)</span></span>
          <select name="level" value={form.level} onChange={handleChange}>
            <option value="">Any</option>
            {zone.levels.map((l) => (
              <option key={l} value={l}>Level {l}</option>
            ))}
          </select>
          {err("level")}
        </label>

        <label className="field">
          <span>Staying for</span>
          <select name="duration_minutes" value={form.duration_minutes} onChange={handleChange}>
            {DURATIONS.map((m) => (
              <option key={m} value={m}>{fmtDuration(m)}</option>
            ))}
          </select>
          {err("duration_minutes")}
        </label>
      </div>

      <label className="field">
        <span>Note <span className="muted">(optional)</span></span>
        <textarea
          name="note"
          value={form.note}
          onChange={handleChange}
          placeholder="Doing CS1F past papers, come say hi"
          maxLength={200}
          rows={2}
        />
        <span className="counter">{form.note.length}/200</span>
        {err("note")}
      </label>

      <label className="field">
        <span>Contact <span className="muted">(optional, shown publicly)</span></span>
        <input
          name="contact"
          value={form.contact}
          onChange={handleChange}
          placeholder="@instagram, discord#1234…"
          maxLength={100}
        />
        {err("contact")}
      </label>

      <button type="submit" className="btn" disabled={status === "sending"}>
        {status === "sending" ? "Posting…" : "Post to the board"}
      </button>
      <p className="hint">No account needed. We email you a link to confirm.</p>
    </form>
  );
}

export default SessionForm;
