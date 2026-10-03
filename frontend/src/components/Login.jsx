import { useState } from "react";
import { api } from "../api/client.js";

export default function Login({ onAuthenticated }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await api.login(username, password);
      onAuthenticated();
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      setSubmitting(false);
      setPassword("");
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={submit}>
        <div className="brand-mark login-mark">P</div>
        <p className="eyebrow">PATCHGUARD RECOVERYHUB</p>
        <h1>Admin sign in</h1>
        <p className="login-description">Enter your administrator username and password to access this workspace.</p>
        <label className="login-label" htmlFor="admin-username">Username</label>
        <input
          autoComplete="username"
          autoFocus
          id="admin-username"
          maxLength={64}
          onChange={(event) => setUsername(event.target.value)}
          required
          type="text"
          value={username}
        />
        <label className="login-label" htmlFor="admin-password">Administrator password</label>
        <input
          autoComplete="current-password"
          id="admin-password"
          maxLength={1024}
          onChange={(event) => setPassword(event.target.value)}
          required
          type="password"
          value={password}
        />
        {error && <p className="login-error" role="alert">{error}</p>}
        <button className="button button-primary login-submit" disabled={submitting} type="submit">
          {submitting ? "Signing in…" : "Sign in"}
        </button>
        <p className="login-footnote">Sessions expire automatically after 12 hours.</p>
      </form>
    </main>
  );
}
