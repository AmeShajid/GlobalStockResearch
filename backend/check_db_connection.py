"""Phase 0.7 verification: confirm Python can reach the PostgreSQL database.

What it does:
  1. Loads the PostgreSQL password from backend/.env (never hardcoded).
  2. Reads the database name from config/config.yaml (single source of truth).
  3. Opens a SQLAlchemy engine to the local PostgreSQL server and runs a
     trivial query.
  4. Prints "connection ok" on success.

Run from the backend folder with the venv active:
    python check_db_connection.py
"""

from pathlib import Path
import os
import sys

import yaml
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Paths are relative to this file, never hardcoded to C:\Users\...
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
ENV_FILE = BACKEND_DIR / ".env"
CONFIG_FILE = REPO_ROOT / "config" / "config.yaml"

# Standard local PostgreSQL defaults (not tunable thresholds).
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"


def load_database_name() -> str:
    """Read system.database_name from config/config.yaml."""
    config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    try:
        return config["system"]["database_name"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError(
            f"Could not find system.database_name in {CONFIG_FILE}"
        ) from exc


def load_password() -> str:
    """Read POSTGRES_PASSWORD from the environment (.env)."""
    load_dotenv(ENV_FILE)
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password or password == "REPLACE_WITH_YOUR_POSTGRES_PASSWORD":
        raise RuntimeError(
            f"POSTGRES_PASSWORD is not set. Put your real password in {ENV_FILE} "
            "(copied from .env.example) and try again."
        )
    return password


def main() -> int:
    try:
        database_name = load_database_name()
        password = load_password()
    except RuntimeError as exc:
        print(f"setup incomplete: {exc}")
        return 1

    # SQLAlchemy URL; the password is supplied at runtime, not stored in code.
    url = (
        f"postgresql+psycopg2://{DB_USER}:{password}"
        f"@{DB_HOST}:{DB_PORT}/{database_name}"
    )

    try:
        engine = create_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - surface any connection failure clearly
        print(f"connection failed: {exc}")
        return 1

    print("connection ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
