import { useState } from "react";

function SessionForm() {
  const [form, setForm] = useState({
    email: "",
    display_name: "",
    zone: "group",
    duration_minutes: 60,
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  const res = await fetch("http://127.0.0.1:8000/api/sessions/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...form, start_time: new Date().toISOString() }),
  });
  const data = await res.json();
  console.log(res.status, data);
};

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="email"
        value={form.email}
        onChange={handleChange}
        placeholder="your@student.gla.ac.uk"
      />
      <input
        name="display_name"
        value={form.display_name}
        onChange={handleChange}
        placeholder="Your name"
      />
      <select name="zone" value={form.zone} onChange={handleChange}>
        <option value="group">Green — group study</option>
        <option value="quiet">Amber — quiet study</option>
        <option value="silent">Red — silent study</option>
      </select>
      <select name="duration_minutes" value={form.duration_minutes} onChange={handleChange}>
        <option value={30}>30 minutes</option>
        <option value={60}>1 hour</option>
        <option value={90}>1.5 hours</option>
        <option value={120}>2 hours</option>
      </select>
      <button type="submit">Post to the board</button>
    </form>
  );
}

export default SessionForm;