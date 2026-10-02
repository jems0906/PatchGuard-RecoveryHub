import { useRef, useState } from "react";
import { api } from "../api/client.js";

const kinds = [
  ["assets", "Server inventory"],
  ["patches", "WSUS patch report"],
  ["vulnerabilities", "Vulnerability scanner"],
  ["ad_issues", "AD health report"],
  ["vms", "vCenter VM inventory"],
  ["backups", "Rubrik backup report"],
];

export default function DataImporter({ onImported }) {
  const [entity, setEntity] = useState("assets");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const formRef = useRef(null);

  async function submit(event) {
    event.preventDefault();
    if (!file) {
      setMessage("Choose a CSV or JSON file first.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const result = await api.importFile(entity, file);
      setMessage(`${result.imported} ${entity.replace("_", " ")} records imported.`);
      setFile(null);
      formRef.current?.reset();
      await onImported();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form ref={formRef} className="import-form" onSubmit={submit}>
      <label>
        Data source
        <select value={entity} onChange={(event) => setEntity(event.target.value)}>
          {kinds.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </label>
      <label className="file-field">
        CSV or JSON file
        <input type="file" accept=".csv,.json" onChange={(event) => setFile(event.target.files?.[0] || null)} />
      </label>
      <button className="button button-primary" disabled={busy}>{busy ? "Importing…" : "Import data"}</button>
      {message && <p className="import-message" role="status">{message}</p>}
      <p className="field-hint">Imports append records. Maximum file size: 5 MB.</p>
    </form>
  );
}
