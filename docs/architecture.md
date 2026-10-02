# Architecture

PatchGuard RecoveryHub is a three-part sample application:

- **React + Vite** provides the responsive operational dashboard and CSV/JSON upload flow.
- **FastAPI** provides read APIs, asset creation, vulnerability status updates, and validated report ingestion.
- **SQLAlchemy** persists records in PostgreSQL in hosted use, with SQLite as the default local development database.

## Data flow

WSUS-style, scanner, Active Directory, vCenter, and backup reports are exported by an operator and uploaded to `/api/imports`. The API parses and validates the report, then commits the batch transactionally. Dashboards calculate patching, vulnerability, backup, AD, VM, and weighted compliance indicators from the imported records. Synthetic demo rows are seeded on a fresh database by default.

## Boundaries

The product is an inventory/compliance tracker, not an infrastructure control plane. It does not connect to Windows, WSUS, Active Directory, vCenter, or Rubrik, and it does not execute patches, restores, account actions, or registry changes. Optional PowerShell samples perform read-only inventory queries only. Deployments handling real infrastructure data need authentication, authorization, audit logging, TLS, data-retention controls, and network restrictions before production use; those controls are outside this demo MVP.

## Deployment

Railway hosts the backend and frontend as separate Docker services and a managed PostgreSQL database, described in `.railway/railway.ts`. The backend's `DATABASE_URL` and frontend's `BACKEND_ORIGIN` use Railway service references. The nginx frontend proxies `/api/` to the backend over Railway private networking. See `docs/railway_deployment.md` for the plan/apply and public-domain steps.
