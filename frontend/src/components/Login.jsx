import { useState } from "react";
import { api } from "../api/client.js";

export default function Login({ onAuthenticated }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await api.login(password);
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
        <p className="login-description">Enter the administrator password to access this workspace.</p>
        <label className="login-label" htmlFor="admin-password">Administrator password</label>
        <input
          autoComplete="current-password"
          autoFocus
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
