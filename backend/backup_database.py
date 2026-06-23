"""Phase 0.8: back up the threadpulse PostgreSQL database with pg_dump.

What it does:
  1. Reads the database name and backup location from config/config.yaml
     (single source of truth; never hardcoded).
  2. Reads the PostgreSQL password from backend/.env (never hardcoded, never
     committed, never placed on the command line).
  3. Runs pg_dump in custom/compressed format (-Fc) to write a timestamped
     dump file into the local backups/ folder.
  4. If an offsite backup location is configured, copies the dump there too —
     a backup that only lives on the same machine is not a real backup.

pg_dump must be callable from PATH (PostgreSQL 16 bin directory was added in
Phase 0.1). This script never uses an absolute path to pg_dump.

Run from the backend folder with the venv active:
    python backup_database.py
"""

from datetime import datetime, timezone
from pathlib import Path
import os
import shutil
import subprocess
import sys

import yaml
from dotenv import load_dotenv


# Paths are relative to this file, never hardcoded to C:\Users\...
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent
ENV_FILE = BACKEND_DIR / ".env"
CONFIG_FILE = REPO_ROOT / "config" / "config.yaml"

# Standard local PostgreSQL defaults (not tunable thresholds).
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"


def load_config() -> dict:
    """Read and parse config/config.yaml."""
    return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))


def get_config_value(config: dict, section: str, key: str) -> str:
    """Pull config[section][key], with a clear error if it is missing."""
    try:
        return config[section][key]
    except (KeyError, TypeError) as exc:
        raise RuntimeError(
            f"Could not find {section}.{key} in {CONFIG_FILE}"
        ) from exc


def load_password() -> str:
    """Read POSTGRES_PASSWORD from the environment (.env)."""
    load_dotenv(ENV_FILE)
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password or password == "your-postgres-password-here":
        raise RuntimeError(
            f"POSTGRES_PASSWORD is not set. Put your real password in {ENV_FILE} "
            "(copied from .env.example) and try again."
        )
    return password


def resolve_backup_dir(config: dict) -> Path:
    """Resolve system.backup_location (relative to the repo root) and create it."""
    raw = get_config_value(config, "system", "backup_location")
    backup_dir = Path(raw)
    if not backup_dir.is_absolute():
        backup_dir = REPO_ROOT / backup_dir
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def resolve_offsite_dir(config: dict) -> Path | None:
    """Resolve the optional offsite backup location.

    Returns None when system.offsite_backup_location is missing or blank, so
    the offsite copy is simply skipped until a real path is configured.
    """
    system = config.get("system", {}) if isinstance(config, dict) else {}
    raw = system.get("offsite_backup_location")
    if not raw or not str(raw).strip():
        return None
    return Path(str(raw).strip())


def run_backup() -> Path:
    """Create one compressed dump of the database and return its path.

    Raises RuntimeError on any failure so callers (and the scheduler) can log it.
    """
    config = load_config()
    database_name = get_config_value(config, "system", "database_name")
    password = load_password()
    backup_dir = resolve_backup_dir(config)

    # UTC timestamp in the filename (Critical Rule #3: all timestamps in UTC).
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dump_path = backup_dir / f"{database_name}_{stamp}.dump"

    # pg_dump is called from PATH (no absolute path). -Fc = custom/compressed
    # format, restorable later with pg_restore.
    command = [
        "pg_dump",
        "--host", DB_HOST,
        "--port", DB_PORT,
        "--username", DB_USER,
        "--format", "custom",
        "--file", str(dump_path),
        database_name,
    ]

    # Pass the password to pg_dump via PGPASSWORD in the subprocess environment
    # only — never on the command line (visible in process lists) and never
    # logged.
    env = dict(os.environ)
    env["PGPASSWORD"] = password

    print(f"Starting backup of '{database_name}' -> {dump_path}")
    result = subprocess.run(
        command,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # pg_dump writes diagnostics to stderr; surface it without the password.
        raise RuntimeError(
            f"pg_dump failed (exit {result.returncode}): {result.stderr.strip()}"
        )

    size_mb = dump_path.stat().st_size / (1024 * 1024)
    print(f"Backup complete: {dump_path} ({size_mb:.2f} MB)")

    copy_offsite(config, dump_path)
    return dump_path


def copy_offsite(config: dict, dump_path: Path) -> None:
    """Copy the dump to the offsite location, if one is configured."""
    offsite_dir = resolve_offsite_dir(config)
    if offsite_dir is None:
        print(
            "Offsite copy skipped: system.offsite_backup_location is not set. "
            "Set it in config/config.yaml to enable real off-machine backups."
        )
        return

    try:
        offsite_dir.mkdir(parents=True, exist_ok=True)
        destination = offsite_dir / dump_path.name
        shutil.copy2(dump_path, destination)
        print(f"Offsite copy complete: {destination}")
    except OSError as exc:
        # An offsite failure (e.g. external drive unplugged) must not throw away
        # the good local backup — log it and carry on.
        print(f"WARNING: offsite copy failed: {exc}")


def main() -> int:
    try:
        run_backup()
    except RuntimeError as exc:
        print(f"backup failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
