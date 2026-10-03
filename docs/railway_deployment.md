# Railway deployment and access control

## Live deployment

The Railway project `PatchGuard RecoveryHub`, environment `production`, runs:

- `postgres`: Railway-managed PostgreSQL, private to the project.
- `backend`: FastAPI on port `8000`, reachable from the frontend over Railway private networking.
- `frontend`: nginx/React, publicly served at <https://frontend-production-724d2.up.railway.app>.

The frontend is the only public service. nginx sends `/api/` requests to `backend.railway.internal:8000`. The public domain routes to container port `8080`.

## Administrator login secrets

The Railway backend must have these variables set in its service settings:

- `AUTH_REQUIRED=true`
- `AUTH_COOKIE_SECURE=true`
- `AUTH_ADMIN_USERNAME`: the administrator username (currently `admin`).
- `AUTH_ADMIN_PASSWORD`: a randomly generated password with at least 32 characters.
- `AUTH_SESSION_SECRET`: an independent, randomly generated secret with at least 32 characters.
- `CORS_ORIGINS=https://frontend-production-724d2.up.railway.app`

The IaC definition enables authentication and preserves the configured username and secret values without storing credentials in source control. Set or rotate them using Railway's secret-variable interface or CLI. The app refuses to start with authentication enabled if the username is blank or either secret is shorter than 32 characters. After changing a variable, allow Railway to redeploy the backend.

The sign-in endpoint is `POST /api/auth/login`. It sets a signed, HttpOnly, SameSite=Strict cookie; HTTPS requests receive a Secure cookie. Sessions expire after 12 hours. `POST /api/auth/logout` clears the session. Health checks remain available at `/api/health`; `/api/auth/session` reports whether a browser has a valid session. Other API endpoints and API docs require a session. Mutating requests must include an allowed same-origin Origin header.

If the admin password is lost, replace `AUTH_ADMIN_PASSWORD` in Railway with a new random value. To invalidate every active session, also rotate `AUTH_SESSION_SECRET`. Keep both values out of Git, issue trackers, screenshots, and logs.

## Previewing infrastructure changes

The checked-in [`.railway/railway.ts`](../.railway/railway.ts) declares the database and both services. From the repository root, use the Railway CLI:

```powershell
railway status
railway config plan
```

Review the exact project, environment, source branch, and any planned creates, updates, or removals before applying. The existing production project already contains the three resources listed above. A future plan should not unexpectedly recreate or delete them.

Only after reviewing the plan and approving its effects, run:

```powershell
railway config apply
```

Applying changes can redeploy services or incur hosting/database charges. Never commit credentials or paste secret values into the IaC file.

## Smoke checks and operational cautions

Verify the public page loads and that `https://frontend-production-724d2.up.railway.app/api/health` returns:

```json
{"status":"ok","service":"PatchGuard RecoveryHub"}
```

The health endpoint is intentionally public for Railway's health checks. The dashboard and write APIs should redirect to the admin sign-in screen or return `401` until a valid session is established. Check Railway logs for service startup errors, but never log passwords, cookies, or session secrets.

The database currently contains synthetic demo data. `SEED_DEMO_DATA=true` remains enabled; changing it to `false` stops future seeding but does not remove existing demo rows. Clear or replace demo records only after reviewing a database backup and the intended data-retention policy.

This deployment uses one shared administrator password. It does not provide individual accounts, role-based authorization, durable audit records for each data change, automated retention, or an application-level backup/restore workflow. Authentication outcomes are written to service logs, whose retention depends on Railway. Do not upload real server, identity, vulnerability, or backup inventories until your organization has approved the residual risks and required controls.
