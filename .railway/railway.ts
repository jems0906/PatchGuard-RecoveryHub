import { defineRailway, github, postgres, preserve, project, ref, service } from "railway/iac";

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
      AUTH_REQUIRED: "true",
      AUTH_COOKIE_SECURE: "true",
      AUTH_ADMIN_USERNAME: preserve(),
      AUTH_ADMIN_PASSWORD: preserve(),
      AUTH_SESSION_SECRET: preserve(),
      CORS_ORIGINS: "https://frontend-production-724d2.up.railway.app",
    },
  });
  const frontend = service("frontend", {
    source: sourceFor("frontend"),
    healthcheck: "/",
    env: {
      BACKEND_ORIGIN: ref(backend, "RAILWAY_PRIVATE_DOMAIN"),
    },
  });

  return project("patchguard-recoveryhub", {
    resources: [database, backend, frontend],
  });
});
