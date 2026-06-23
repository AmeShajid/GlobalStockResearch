"""Phase 0.10 verification: validate the whole Milestone 0 environment.

What it does:
  Runs one check per Milestone 0 requirement and prints a PASS / WARN / FAIL
  line for each. It exits with code 1 if any CORE check fails, so you can tell
  at a glance whether the environment is ready to start Milestone 1.

  CORE checks (must pass — exit 1 if any fail):
    - Python is 3.11.x
    - config/config.yaml loads cleanly
    - PostgreSQL is reachable from Python
    - the virtual environment is active

  SUPPORTING checks (reported as WARN if missing — needed by later milestones,
  not by the start of Milestone 1):
    - Node.js 20.x          (dashboard, Milestone 7)
    - psql 16.x on PATH     (Postgres client)
    - pg_dump on PATH       (backups, Phase 0.8)
    - git connected to GitHub
    - Ollama present        (summaries, Milestone 7)
    - system sleep disabled while plugged in (Phase 0.9)

Run from the backend folder with the venv active:
    python validate_environment.py
"""

from pathlib import Path
import os
import subprocess
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


def _run(command: list[str]) -> tuple[bool, str]:
    """Run a command and return (succeeded, combined output text).

    Returns (False, "") if the executable is not found on PATH so callers can
    report a clean WARN instead of crashing.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except FileNotFoundError:
        return False, ""
    except subprocess.SubprocessError as exc:
        return False, str(exc)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


# --- CORE checks ----------------------------------------------------------


def check_python_version() -> tuple[str, str]:
    """Python must be 3.11.x (the pinned project runtime)."""
    major, minor, micro = sys.version_info[:3]
    detail = f"Python {major}.{minor}.{micro}"
    ok = (major == 3) and (minor == 11)
    return ("PASS" if ok else "FAIL"), detail


def check_config_loads() -> tuple[str, str]:
    """config/config.yaml must exist and parse as YAML."""
    if not CONFIG_FILE.exists():
        return "FAIL", f"missing {CONFIG_FILE}"
    try:
        data = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return "FAIL", f"could not parse config.yaml: {exc}"
    if not isinstance(data, dict) or "system" not in data:
        return "FAIL", "config.yaml parsed but is missing the 'system' section"
    return "PASS", "config.yaml loaded"


def check_database_reachable() -> tuple[str, str]:
    """Python must be able to connect to the local PostgreSQL database."""
    try:
        config = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
        database_name = config["system"]["database_name"]
    except (OSError, yaml.YAMLError, KeyError, TypeError) as exc:
        return "FAIL", f"could not read database name from config: {exc}"

    load_dotenv(ENV_FILE)
    password = os.environ.get("POSTGRES_PASSWORD")
    if not password or password == "REPLACE_WITH_YOUR_POSTGRES_PASSWORD":
        return "FAIL", f"POSTGRES_PASSWORD not set in {ENV_FILE}"

    url = (
        f"postgresql+psycopg2://{DB_USER}:{password}"
        f"@{DB_HOST}:{DB_PORT}/{database_name}"
    )
    try:
        engine = create_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - surface any connection failure
        return "FAIL", f"connection failed: {exc}"
    return "PASS", f"connected to '{database_name}'"


def check_virtualenv_active() -> tuple[str, str]:
    """The project virtual environment should be active."""
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv or os.environ.get("VIRTUAL_ENV"):
        return "PASS", f"venv active at {sys.prefix}"
    return "FAIL", "no virtual environment active (run .\\.venv\\Scripts\\Activate.ps1)"


# --- SUPPORTING checks ----------------------------------------------------


def check_node_version() -> tuple[str, str]:
    """Node.js 20.x is needed for the dashboard (Milestone 7)."""
    ok, output = _run(["node", "--version"])
    if not ok:
        return "WARN", "node not found on PATH (needed in Milestone 7)"
    # output looks like "v20.11.1"
    version = output.lstrip("v")
    if version.startswith("20."):
        return "PASS", f"Node {version}"
    return "WARN", f"Node {version} (blueprint expects 20.x)"


def check_psql_version() -> tuple[str, str]:
    """psql 16.x client should be on PATH."""
    ok, output = _run(["psql", "--version"])
    if not ok:
        return "WARN", "psql not found on PATH"
    if "16." in output:
        return "PASS", output
    return "WARN", f"{output} (blueprint expects 16.x)"


def check_pg_dump_available() -> tuple[str, str]:
    """pg_dump must be on PATH for the Phase 0.8 nightly backup."""
    ok, output = _run(["pg_dump", "--version"])
    if not ok:
        return "WARN", "pg_dump not found on PATH (needed by backup script)"
    return "PASS", output


def check_git_remote() -> tuple[str, str]:
    """Git should be connected to a GitHub remote."""
    ok, output = _run(["git", "-C", str(REPO_ROOT), "remote", "-v"])
    if not ok:
        return "WARN", "git not found or no remote configured"
    if "github.com" in output:
        return "PASS", "git remote points to GitHub"
    return "WARN", "git remote is not a GitHub URL"


def check_ollama_present() -> tuple[str, str]:
    """Ollama is used for summaries in Milestone 7 — presence check only."""
    ok, output = _run(["ollama", "--version"])
    if not ok:
        return "WARN", "ollama not found on PATH (needed in Milestone 7)"
    return "PASS", output


def check_sleep_disabled() -> tuple[str, str]:
    """Phase 0.9: system sleep while plugged in (AC) should be Never.

    powercfg reports the AC standby-idle timeout as a hex value; 0 means Never.
    Only runs on Windows; reports WARN elsewhere.
    """
    if not sys.platform.startswith("win"):
        return "WARN", "sleep check only runs on Windows"
    ok, output = _run(
        ["powercfg", "/query", "SCHEME_CURRENT", "SUB_SLEEP", "STANDBYIDLE"]
    )
    if not ok:
        return "WARN", "could not read powercfg sleep setting"
    ac_index = None
    for line in output.splitlines():
        if "Current AC Power Setting Index" in line:
            ac_index = line.split(":")[-1].strip()
            break
    if ac_index is None:
        return "WARN", "could not find AC sleep setting in powercfg output"
    # Hex like 0x00000000 -> 0 means "Never".
    try:
        seconds = int(ac_index, 16)
    except ValueError:
        return "WARN", f"unexpected powercfg value: {ac_index}"
    if seconds == 0:
        return "PASS", "system sleep is Never while plugged in"
    minutes = seconds // 60
    return "WARN", f"system sleeps after {minutes} min on AC (should be Never)"


# Each entry: (label, function, is_core)
CHECKS = [
    ("Python 3.11.x", check_python_version, True),
    ("config.yaml loads", check_config_loads, True),
    ("PostgreSQL reachable", check_database_reachable, True),
    ("virtualenv active", check_virtualenv_active, True),
    ("Node.js 20.x", check_node_version, False),
    ("psql 16.x", check_psql_version, False),
    ("pg_dump on PATH", check_pg_dump_available, False),
    ("git -> GitHub", check_git_remote, False),
    ("Ollama present", check_ollama_present, False),
    ("sleep disabled (AC)", check_sleep_disabled, False),
]


def main() -> int:
    print("ThreadPulse - Phase 0.10 environment validation\n")
    core_failed = False
    label_width = max(len(label) for label, _, _ in CHECKS)

    for label, func, is_core in CHECKS:
        try:
            status, detail = func()
        except Exception as exc:  # noqa: BLE001 - never let one check crash the run
            status, detail = "FAIL", f"unexpected error: {exc}"
        tag = "core" if is_core else "    "
        print(f"  [{status}] {tag}  {label.ljust(label_width)}  {detail}")
        if is_core and status == "FAIL":
            core_failed = True

    print()
    if core_failed:
        print("RESULT: core checks FAILED — fix the FAIL lines above before Milestone 1.")
        return 1
    print("RESULT: all core checks passed - environment is ready for Milestone 1.")
    print("        (Any WARN lines are for later milestones; address when you reach them.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
