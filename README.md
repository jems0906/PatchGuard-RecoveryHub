# PatchGuard RecoveryHub

An infrastructure compliance dashboard for Windows server patch status, vulnerability remediation, Active Directory hygiene, VMware VM health, and backup validation. It uses **FastAPI + SQLAlchemy**, **React + Vite + Recharts**, and supports **PostgreSQL** (with SQLite for local development).

> This project tracks imported operational reports; it does not connect to or make changes to WSUS, Windows, Active Directory, vCenter, or Rubrik. The bundled data is synthetic. Do not upload production infrastructure information to an unauthenticated/public deployment.

## Included

- Weighted compliance overview, 30-day trend, patch compliance, overdue vulnerability and high-risk system indicators.
- Server and VM inventory, WSUS-style deployment statuses, vulnerability lifecycle tracking, AD health findings, backup/SLA summaries, VM health alerts.
- CSV/JSON import for assets, patches, vulnerabilities, AD issues, VMs, and backups.
- Sample reports in [`data_samples/`](./data_samples), read-only optional PowerShell collectors in [`scripts/powershell/`](./scripts/powershell), and operational runbooks in [`docs/`](./docs).
- FastAPI OpenAPI docs at `/docs`, pytest API/report tests, Dockerfiles, GitHub Actions, and Railway configuration.

## Run locally

Requirements: Python 3.11+ and Node.js 20.19+.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`; interactive docs are at `http://localhost:8000/docs`. A fresh local database is seeded with synthetic demo rows by default. Set `SEED_DEMO_DATA=false` to disable demo seeding. Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL to use PostgreSQL. For schema migrations, run `alembic upgrade head` from `backend/`.

### Frontend

In another PowerShell terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to `http://localhost:8000`. For a separately hosted API, set `VITE_API_BASE_URL` to the API origin before starting/building the frontend.

## Import sample reports

The seeded database is immediately usable. To import the checked-in reports into an empty database (imports append and do not deduplicate), start the backend and run from the repository root:

```powershell
python scripts/import_all.py
```

Set `PATCHGUARD_API_URL` when the API is not at `http://localhost:8000/api`. Each CSV has headers matching the API model fields. JSON imports accept an array of records or `{"records": [...]}`. An upload is limited to 5 MB; invalid rows abort the entire batch. See API docs for the current schema.

Generate reproducible lab-only CSV data in `data_samples/generated/` with `python scripts/generate_synthetic_infra_data.py --count 25 --seed 7`. Use `--output <directory>` to choose another destination.

To seed an empty local SQLite database without starting the API, run `python scripts/seed_database.py` from the repository root. It seeds the backend database unless `DATABASE_URL` is already set.

## Tests and build

```powershell
cd backend
python -m pytest -q
cd ..\frontend
npm run build
```

## Docker and Railway

Build the backend from `backend/` and the frontend from `frontend/`; the frontend nginx container serves the single-page app and proxies `/api` requests. Set `BACKEND_ORIGIN` in the frontend service to the backend's reachable URL (including `http://` or `https://`).

For Railway, follow the step-by-step [deployment preparation guide](./docs/railway_deployment.md). The checked-in [`.railway/railway.ts`](./.railway/railway.ts) defines the Railway-managed PostgreSQL database plus backend and frontend services. The repository slug and target Railway project/environment must be supplied/reviewed before running `railway config plan` and `railway config apply`. A public frontend domain is generated in the Railway dashboard after provisioning. Do not expose sensitive inventory data until authentication, authorization, audit logging, and access controls have been added.

## Operational guides

- [WSUS patch management](./docs/wsus_patch_management_runbook.md)
- [Vulnerability remediation](./docs/vulnerability_remediation_runbook.md)
- [Active Directory troubleshooting](./docs/active_directory_troubleshooting_runbook.md)
- [VMware operations](./docs/vmware_operations_runbook.md)
- [Backup validation](./docs/backup_validation_runbook.md)
- [Change record template](./docs/change_record_template.md)
- [Architecture and security boundaries](./docs/architecture.md)

## API outline

`GET /api/health`, `/api/compliance/overview`, `/api/compliance/trend`, `/api/assets`, `/api/patches`, `/api/patches/compliance`, `/api/vulnerabilities`, `/api/ad/health`, `/api/ad/issues`, `/api/ad/actions`, `/api/vms`, `/api/vms/alerts`, `/api/backups`, `/api/backups/sla`, `/api/backups/readiness`. Create assets, patches, vulnerabilities, and AD action audit records with `POST`; update remediation status via `PATCH /api/vulnerabilities/{id}`; upload reports via `POST /api/imports?entity=<entity>`.

## Scoring notes

The overall score weights patching 35%, vulnerability remediation 30%, backup SLA status 25%, and AD hygiene 10%. A patch is counted for the patch rate when its classification is critical/security and its status is installed. Backup freshness uses demo windows of 2 hours for Gold, 26 hours for Silver, and 8 days for Bronze. An empty category is treated as 100% until records are imported. The demo AD hygiene indicator subtracts ten points per open issue (floored at zero); tune thresholds and scoring to your organization's approved compliance methodology before operational use.
