import { defineRailway, github, postgres, project, service } from "railway/iac";

const repository = "jems0906/PatchGuard-RecoveryHub";
const branch = process.env.GITHUB_BRANCH || "main";
const sourceFor = (rootDirectory: string) =>
  github(repository, {
    rootDirectory,
    branch,
  });

export default defineRailway(() => {
  const database = postgres("postgres");
  const backend = service("backend", {
    source: sourceFor("backend"),
    healthcheck: "/api/health",
    env: {
      DATABASE_URL: database.env.DATABASE_URL,
      PORT: "8000",
      SEED_DEMO_DATA: "true",
    },
  });
  const frontend = service("frontend", {
    source: sourceFor("frontend"),
    healthcheck: "/",
    env: {
      BACKEND_ORIGIN: `http://${backend.env.RAILWAY_PRIVATE_DOMAIN}:8000`,
    },
  });

  return project("patchguard-recoveryhub", {
    resources: [database, backend, frontend],
  });
});
