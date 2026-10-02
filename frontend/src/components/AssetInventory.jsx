import { useMemo, useState } from "react";

export default function AssetInventory({ assets }) {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => assets.filter((asset) =>
    [asset.hostname, asset.role, asset.os_version, asset.domain, asset.forest, asset.site, asset.fsmo_roles, asset.ip_address]
      .some((value) => value?.toLowerCase().includes(query.toLowerCase())),
  ), [assets, query]);
  return (
    <>
      <div className="toolbar">
        <div><p className="eyebrow">CONFIGURATION INVENTORY</p><h2>Server assets <span className="count-pill">{assets.length}</span></h2></div>
        <input className="search-input" aria-label="Search assets" placeholder="Search assets…" value={query} onChange={(event) => setQuery(event.target.value)} />
      </div>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Hostname</th><th>Role</th><th>Operating system</th><th>IP address</th><th>Domain / forest</th><th>AD site</th><th>FSMO roles</th><th>Last boot</th><th>Backup policy</th></tr></thead>
          <tbody>
            {filtered.map((asset) => <tr key={asset.id}><td className="primary-cell">{asset.hostname}</td><td>{asset.role}</td><td>{asset.os_version}</td><td>{asset.ip_address || "—"}</td><td>{asset.domain || "—"}{asset.forest && asset.forest !== asset.domain ? ` / ${asset.forest}` : ""}</td><td>{asset.site || "—"}</td><td>{asset.fsmo_roles || "—"}</td><td>{asset.last_boot || "—"}</td><td>{asset.backup_policy || "—"}</td></tr>)}
            {!filtered.length && <tr><td className="empty-cell" colSpan="9">No matching assets found.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}
