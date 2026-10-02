import sys
import os
from pathlib import Path
from sqlalchemy.engine import URL

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault(
    "DATABASE_URL",
    URL.create("sqlite", database=str(ROOT / "backend" / "patchguard.db")).render_as_string(hide_password=False),
)
sys.path.insert(0, str(ROOT / "backend"))

from app.database import SessionLocal, engine  # noqa: E402
from app.models import Base  # noqa: E402
from app.seed import seed_demo_data  # noqa: E402

Base.metadata.create_all(bind=engine)
with SessionLocal() as session:
    seed_demo_data(session)
print("Demo records seeded if the database was empty.")
