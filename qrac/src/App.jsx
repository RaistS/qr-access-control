import React, { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:3000";

export default function App() {
  const [health, setHealth] = useState("checking…");
  const [events, setEvents] = useState([]);
  const [newEvent, setNewEvent] = useState("");
  const [guests, setGuests] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [guestForm, setGuestForm] = useState({ name: "", email: "" });
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  async function getJSON(url, opts) {
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }

  const loadHealth = () =>
    getJSON(`${API}/health/ping`).then(() => setHealth("ok")).catch(() => setHealth("error"));

  const loadEvents = () =>
    getJSON(`${API}/events/`).then(setEvents);

  const loadGuests = (eventId) =>
    getJSON(`${API}/guests/?event_id=${eventId}`).then(setGuests);

  useEffect(() => { loadHealth(); loadEvents(); }, []);

  async function createEvent(e) {
    e.preventDefault();
    if (!newEvent.trim()) return;
    setBusy(true);
    try {
      await getJSON(`${API}/events/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newEvent }),
      });
      setNewEvent("");
      await loadEvents();
      setMsg("Evento creado ✅");
    } catch (err) {
      setMsg(`Error creando evento: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function createGuest(e) {
    e.preventDefault();
    if (!selectedEvent) return setMsg("Selecciona un evento");
    setBusy(true);
    try {
      const g = await getJSON(`${API}/guests/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: guestForm.name,
          email: guestForm.email,
          event_id: selectedEvent.id,
        }),
      });
      await loadGuests(selectedEvent.id);
      setGuestForm({ name: "", email: "" });
      setMsg(`Invitado creado (id ${g.id}) ✅`);
    } catch (err) {
      setMsg(`Error creando invitado: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "system-ui, sans-serif" }}>
      <h1>QR Access Control — Front</h1>
      <p>API: {API} | health: <b>{health}</b></p>

      <section style={{ padding: 16, border: "1px solid #eee", borderRadius: 12, marginBottom: 16 }}>
        <h2>Eventos</h2>
        <form onSubmit={createEvent} style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <input
            placeholder="Nombre del evento"
            value={newEvent}
            onChange={(e) => setNewEvent(e.target.value)}
            style={{ flex: 1, padding: 8 }}
          />
          <button disabled={busy}>Crear</button>
        </form>
        <ul>
          {events.map(ev => (
            <li key={ev.id} style={{ marginBottom: 6 }}>
              <button onClick={() => { setSelectedEvent(ev); loadGuests(ev.id); }}>
                Seleccionar
              </button>{" "}
              <b>#{ev.id}</b> — {ev.name} {ev.date ? `(${new Date(ev.date).toLocaleString()})` : ""}
            </li>
          ))}
        </ul>
      </section>

      {selectedEvent && (
        <section style={{ padding: 16, border: "1px solid #eee", borderRadius: 12, marginBottom: 16 }}>
          <h2>Invitados — Evento #{selectedEvent.id} · {selectedEvent.name}</h2>

          <form onSubmit={createGuest} style={{ display: "flex", gap: 8, marginBottom: 12 }}>
            <input
              placeholder="Nombre"
              value={guestForm.name}
              onChange={(e) => setGuestForm({ ...guestForm, name: e.target.value })}
              style={{ flex: 1, padding: 8 }}
            />
            <input
              placeholder="Email"
              value={guestForm.email}
              onChange={(e) => setGuestForm({ ...guestForm, email: e.target.value })}
              style={{ flex: 1, padding: 8 }}
              type="email"
            />
            <button disabled={busy}>Añadir invitado</button>
          </form>

          <ul>
            {guests.map(g => (
              <li key={g.id} style={{ marginBottom: 8 }}>
                <b>{g.name}</b> — {g.email} · token: <code>{g.token}</code>{" "}
                <a href={`${API}/guests/qr/${g.id}.png`} target="_blank" rel="noreferrer">Ver QR</a>
              </li>
            ))}
          </ul>
        </section>
      )}

      {msg && <p><i>{msg}</i></p>}
    </div>
  );
}
