const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}/api${path}`, {
    credentials: "same-origin",
    ...options,
  });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the HTTP status message when the server did not return JSON.
    }
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

export const api = {
  session: () => request("/auth/session"),
  login: (username, password) => request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  }),
  logout: () => request("/auth/logout", { method: "POST" }),
  health: () => request("/health"),
  overview: () => request("/compliance/overview"),
  trend: () => request("/compliance/trend"),
  assets: () => request("/assets"),
  patches: () => request("/patches"),
  vulnerabilities: () => request("/vulnerabilities"),
  adHealth: () => request("/ad/health"),
  adActions: () => request("/ad/actions"),
  recordAdAction: (payload) => request("/ad/actions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }),
  vms: () => request("/vms"),
  vmAlerts: () => request("/vms/alerts"),
  backups: () => request("/backups"),
  recoveryReadiness: () => request("/backups/readiness"),
  verifyVulnerability: (id) =>
    request(`/vulnerabilities/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "verified", verified_by: "Dashboard operator", verified_at: new Date().toISOString().slice(0, 10) }),
    }),
  importFile: (entity, file) => {
    const form = new FormData();
    form.append("file", file);
    return request(`/imports?entity=${encodeURIComponent(entity)}`, { method: "POST", body: form });
  },
};
