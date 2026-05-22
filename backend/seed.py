"""
Runs at container startup (before uvicorn):
  1. Creates all SQLAlchemy tables (idempotent).
  2. Applies seed.sql using INSERT OR IGNORE, so re-runs are safe.
"""

import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

# Register models and create tables
from src.database.sqlite_config import Base, engine  # noqa: E402
import src.modules.ticket.model  # noqa: F401
import src.modules.auth.model    # noqa: F401

Base.metadata.create_all(bind=engine)

# Resolve the SQLite file path from DATABASE_URL
# Handles both forms:
#   sqlite:////data/tonhao.db  (absolute, 4 slashes)
#   sqlite:///./tonhao.db      (relative, 3 slashes)
db_url = os.getenv("DATABASE_URL", "sqlite:///./tonhao.db")
db_path = db_url.replace("sqlite:///", "", 1)

seed_path = os.path.join(os.path.dirname(__file__), "seed.sql")
with open(seed_path, encoding="utf-8") as f:
    sql = f.read()

conn = sqlite3.connect(db_path)
conn.executescript(sql)
conn.close()

print(f"Seed applied to '{db_path}' successfully.")
