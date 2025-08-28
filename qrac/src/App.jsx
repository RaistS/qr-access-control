import React, { useEffect, useState } from "react";
import "./App.css";

const API = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export default function App() {
  const [health, setHealth] = useState("checking…");
  const [events, setEvents] = useState([]);
  const [newEvent, setNewEvent] = useState("");
  const [guests, setGuests] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [guestForm, setGuestForm] = useState({ name: "", email: "" });
  const [csvFile, setCsvFile] = useState(null);
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

  // load initial data
  // eslint-disable-next-line react-hooks/exhaustive-deps
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

  async function sendQR(guestId) {
    setBusy(true);
    try {
      await getJSON(`${API}/guests/${guestId}/resend`, { method: "POST" });
      setMsg("QR enviado por email ✅");
    } catch (err) {
      setMsg(`Error enviando QR: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function importGuests(e) {
    e.preventDefault();
    if (!selectedEvent || !csvFile) return;
    setBusy(true);
    try {
      const fd = new FormData();
      fd.append("file", csvFile);
      await fetch(`${API}/guests/import?event_id=${selectedEvent.id}`, {
        method: "POST",
        body: fd,
      }).then((r) => {
        if (!r.ok) throw new Error("import failed");
        return r.json();
      });
      await loadGuests(selectedEvent.id);
      setCsvFile(null);
      setMsg("Invitados importados ✅");
    } catch (err) {
      setMsg(`Error importando invitados: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container">
      <h1>QR Access Control — Front</h1>
      <p>
        API: {API} | health: <b>{health}</b>
      </p>

      <section className="section">
        <h2>Eventos</h2>
        <form onSubmit={createEvent} className="form">
          <input
            placeholder="Nombre del evento"
            value={newEvent}
            onChange={(e) => setNewEvent(e.target.value)}
            className="input"
          />
          <button className="button" disabled={busy}>Crear</button>
        </form>
        <ul className="events-list">
          {events.map((ev) => (
            <li key={ev.id}>
              <button onClick={() => { setSelectedEvent(ev); loadGuests(ev.id); }}>
                Seleccionar
              </button>{" "}
              <b>#{ev.id}</b> — {ev.name} {ev.date ? `(${new Date(ev.date).toLocaleString()})` : ""}
            </li>
          ))}
        </ul>
      </section>

      {selectedEvent && (
        <section className="section">
          <h2>
            Invitados — Evento #{selectedEvent.id} · {selectedEvent.name}
          </h2>

          <form onSubmit={createGuest} className="form">
            <input
              placeholder="Nombre"
              value={guestForm.name}
              onChange={(e) => setGuestForm({ ...guestForm, name: e.target.value })}
              className="input"
            />
            <input
              placeholder="Email"
              value={guestForm.email}
              onChange={(e) => setGuestForm({ ...guestForm, email: e.target.value })}
              className="input"
              type="email"
            />
            <button className="button" disabled={busy}>Añadir invitado</button>
          </form>

          <form onSubmit={importGuests} className="form">
            <input type="file" accept=".csv" onChange={(e) => setCsvFile(e.target.files[0])} />
            <button className="button" disabled={busy || !csvFile}>Importar CSV</button>
          </form>

          <ul className="guest-list">
            {guests.map((g) => (
              <li key={g.id}>
                <b>{g.name}</b> — {g.email} · token: <code>{g.token}</code>{" "}
                <a href={`${API}/guests/qr/${g.id}.png`} target="_blank" rel="noreferrer">
                  Ver QR
                </a>{" "}
                <button onClick={() => sendQR(g.id)} disabled={busy}>
                  Enviar QR por email
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {msg && (
        <p>
          <i>{msg}</i>
        </p>
      )}
    </div>
  );
}
