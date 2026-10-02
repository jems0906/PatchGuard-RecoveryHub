import { useState } from "react";
import { api } from "../api/client.js";

const actionTypes = ["Account unlock", "Password reset", "Group membership change", "Computer object cleanup"];

export default function ADActionLog({ actions, onRecorded }) {
  const [form, setForm] = useState({ action_type: actionTypes[0], target: "", actor: "", ticket_reference: "", details: "" });
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      await api.recordAdAction(form);
      setForm({ ...form, target: "", ticket_reference: "", details: "" });
      setMessage("Action record saved. No directory change was performed.");
      await onRecorded();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="ad-action-panel">
      <div className="panel-heading"><div><p className="eyebrow">AUDIT TRAIL</p><h2>AD administrative action log</h2></div></div>
      <p className="action-disclaimer">Record authorized administrative work for audit evidence. This form logs actions only; it does not unlock accounts, reset passwords, edit memberships, or remove objects.</p>
      <form className="action-form" onSubmit={submit}>
        <label>Action<select value={form.action_type} onChange={(event) => setForm({ ...form, action_type: event.target.value })}>{actionTypes.map((action) => <option key={action}>{action}</option>)}</select></label>
        <label>Target<input required value={form.target} onChange={(event) => setForm({ ...form, target: event.target.value })} placeholder="User or computer" /></label>
        <label>Performed by<input required value={form.actor} onChange={(event) => setForm({ ...form, actor: event.target.value })} placeholder="Operator" /></label>
        <label>Ticket / change ID<input required value={form.ticket_reference} onChange={(event) => setForm({ ...form, ticket_reference: event.target.value })} placeholder="CHG-1234" /></label>
        <label className="action-details">Notes<input value={form.details} onChange={(event) => setForm({ ...form, details: event.target.value })} placeholder="Evidence or result" /></label>
        <button className="button button-primary" disabled={busy}>{busy ? "Saving…" : "Record action"}</button>
        {message && <p className="action-message" role="status">{message}</p>}
      </form>
      <div className="table-scroll action-table">
        <table><thead><tr><th>Time (UTC)</th><th>Action</th><th>Target</th><th>Actor</th><th>Ticket</th><th>Notes</th></tr></thead>
          <tbody>{actions.map((action) => <tr key={action.id}><td>{action.created_at}</td><td>{action.action_type}</td><td>{action.target}</td><td>{action.actor}</td><td>{action.ticket_reference}</td><td>{action.details || "—"}</td></tr>)}
            {!actions.length && <tr><td className="empty-cell" colSpan="6">No AD action records yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </section>
  );
}
