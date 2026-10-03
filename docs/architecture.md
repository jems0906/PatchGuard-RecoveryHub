# Architecture

PatchGuard RecoveryHub is a three-part sample application:

- **React + Vite** provides the responsive operational dashboard and CSV/JSON upload flow.
- **FastAPI** provides read APIs, asset creation, vulnerability status updates, and validated report ingestion.
- **SQLAlchemy** persists records in PostgreSQL in hosted use, with SQLite as the default local development database.

## Data flow

WSUS-style, scanner, Active Directory, vCenter, and backup reports are exported by an operator and uploaded to `/api/imports`. The API parses and validates the report, then commits the batch transactionally. Dashboards calculate patching, vulnerability, backup, AD, VM, and weighted compliance indicators from the imported records. Patch approval gates installation-state changes. AD evidence includes explicit enabled/service-account flags and password set/expiry/age values; backup evidence includes schedule cadence and retention days. Synthetic demo rows are seeded on a fresh database by default.

The authenticated compliance overview records at most one score snapshot per calendar day, which supplies the 30-day trend. `/api/compliance/audit` exports a point-in-time JSON package with the summary, operational records, administrator-recorded AD actions, and available snapshots. This is an evidence export, not an immutable event ledger: it does not record every edit, actor, or before/after value. Review the deployment and retention warnings before using it as regulated audit evidence.

## Boundaries

The product is an inventory/compliance tracker, not an infrastructure control plane. It does not connect to Windows, WSUS, Active Directory, vCenter, or Rubrik, and it does not execute patches, restores, account actions, or registry changes. Optional PowerShell samples perform read-only inventory queries only.

When `AUTH_REQUIRED=true`, the API requires a single administrator password for all routes except `/api/health`, `/api/auth/session`, and `/api/auth/login`. Successful login creates a signed, HttpOnly, SameSite=Strict cookie that expires after 12 hours. Mutating requests are checked against their Origin. The Railway deployment enables this gate. Local development leaves it disabled by default; see `.env.example`.

This shared-password gate is not multi-user identity or role-based authorization. Authentication outcomes are written to application logs, but individual data changes are not stored in a durable audit log. Before using real infrastructure records, add organization-approved identity, user-level audit and retention, database backups, and any required network restrictions. The dashboard currently runs with synthetic demo records.

## Deployment

Railway hosts the backend and frontend as separate Docker services and a managed PostgreSQL database, described in `.railway/railway.ts`. The backend's `DATABASE_URL` and frontend's `BACKEND_ORIGIN` use Railway service references. The nginx frontend proxies `/api/` to the backend over Railway private networking. The public frontend uses a Railway domain and prompts for the admin password. See `docs/railway_deployment.md` for live-service details and secret rotation.
