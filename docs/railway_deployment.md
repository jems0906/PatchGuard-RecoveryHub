# Railway deployment preparation

The Railway project definition is in [`.railway/railway.ts`](../.railway/railway.ts). It describes one Railway-managed PostgreSQL database and two Dockerfile services. It connects the frontend proxy to the backend's private Railway hostname; the backend and database do not need public domains.

## Before provisioning

1. Push this project to [`jems0906/PatchGuard-RecoveryHub`](https://github.com/jems0906/PatchGuard-RecoveryHub). The Railway configuration already points to that repository and its `main` branch. The repository must contain both `backend/` and `frontend/`; GitHub currently reports that it is empty (no commits or branches), so it cannot be used as a deploy source until the project files are pushed.
2. Install Railway CLI **5.42.1 or newer** using Railway's [official installation guide](https://docs.railway.com/cli#installing-the-cli), install Node.js/npm, and from the repository root run `npm install`.
3. Log in and link the repository directory to the intended Railway project and environment using `railway login` and `railway link`. Use a **new, empty Railway project/environment** for the first apply. Infrastructure as Code treats the file as the intended complete resource set; an existing project's resources missing from this file may be proposed for removal.
4. If deploying a branch other than `main`, set it in PowerShell:

   ```powershell
   $env:GITHUB_BRANCH = "release"
   ```

   Replace `release` with the intended branch. If omitted, the config uses `main`.
5. Preview first:

   ```powershell
   railway config plan
   ```

   Review the project/environment name, source repository and branch, Docker root directories, database, service variables, and any destructive changes. A first deployment is expected to create billable resources. Do not continue if the plan targets the wrong Railway environment or contains unintentional removals.

## Provision and deploy

After reviewing the plan, run the interactive apply:

```powershell
railway config apply
```

Confirm only the intended creates/changes in Railway's prompt. This will provision the PostgreSQL service and connect/deploy the backend and frontend from GitHub. The backend's Dockerfile runs `alembic upgrade head` before starting FastAPI; the frontend's Dockerfile builds the Vite app and runs nginx. Railway's assigned public frontend port is consumed by nginx; the backend listens on its configured internal port `8000`.

## Public URL and smoke check

1. In Railway, open the **frontend** service's Settings → Networking and generate a Railway public domain. Keep the backend private unless there is a specific operational reason to expose it.
2. Open the frontend domain and check that the dashboard loads. Check `https://<frontend-domain>/api/health` returns `{"status":"ok","service":"PatchGuard RecoveryHub"}`. The frontend nginx proxy sends `/api/` over Railway's private network to the backend.
3. Check Railway deployment logs for both services and verify the backend migration completed before the API started. The database should remain private and accessible through the `DATABASE_URL` service reference.
4. The generated domain is assigned after the first apply, so it is not embedded in source. If the frontend later calls the backend directly from a browser instead of using the nginx proxy, configure backend `CORS_ORIGINS` to allow the exact frontend origin.

## Demo data and real-data caution

`SEED_DEMO_DATA=true` is set for an immediately populated demo. For an empty production database, set it to `false` **before the first backend deployment**. The seed routine only inserts when the asset table is empty; changing this variable does not remove demo rows already seeded.

This MVP has no user authentication or authorization, and its audit-action screen records entries but does not perform Active Directory actions. Do not import production server, user, vulnerability, or backup inventories into a publicly reachable deployment until access control, audit, retention, and organizational security requirements are implemented and verified. Railway provisioning/deployment is not executed by this preparation.

## Configuration implementation notes

- The frontend uses `BACKEND_ORIGIN=http://<backend-private-domain>:8000` and proxies API requests, so no backend public domain or browser CORS exception is needed for normal dashboard use.
- `DATABASE_URL` is a Railway-managed service reference, not a committed secret.
- Each GitHub service source is rooted at its own directory. Railway detects the Dockerfile in that root, preserving the build contexts already tested locally.
- The repository is configured as `jems0906/PatchGuard-RecoveryHub` on `main`. The public frontend domain and Railway project/environment selection still need to be configured/reviewed before applying.

## References

- [Deploying a Railway monorepo](https://docs.railway.com/deployments/monorepo)
- [Railway Infrastructure as Code](https://docs.railway.com/infrastructure-as-code)
- [Infrastructure as Code TypeScript reference](https://docs.railway.com/infrastructure-as-code/reference)
- [Private networking](https://docs.railway.com/networking/private-networking)
- [Health checks](https://docs.railway.com/deployments/healthchecks)
