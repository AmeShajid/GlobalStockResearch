"""Phase 0.8: run the database backup nightly via APScheduler.

This is a small standalone daemon. Start it and leave it running; it triggers
backup_database.run_backup() once a night at the UTC hour configured in
config/config.yaml (system.backup_hour_utc).

APScheduler settings (mirrors the Phase 1.7 convention):
  - coalesce=True: if several nightly runs were missed (PC off/asleep), only one
    catch-up run executes when it comes back, not a burst of missed runs.
  - misfire_grace_time: a run that starts a little late still executes instead
    of being skipped.

Run from the backend folder with the venv active:
    python backup_scheduler.py
Stop it with Ctrl+C.
"""

from datetime import datetime, timezone
import sys

from apscheduler.schedulers.blocking import BlockingScheduler

from backup_database import load_config, get_config_value, run_backup


# How late a missed nightly run may start and still execute (seconds).
MISFIRE_GRACE_TIME_SECONDS = 3600


def scheduled_backup() -> None:
    """Wrapper so one failed run never kills the scheduler."""
    try:
        run_backup()
    except Exception as exc:  # noqa: BLE001 - keep the daemon alive on any error
        print(f"Scheduled backup failed: {exc}")


def main() -> int:
    config = load_config()
    # Nightly hour comes from config (Critical Rule #1: no hardcoded settings).
    backup_hour = int(get_config_value(config, "system", "backup_hour_utc"))

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        scheduled_backup,
        trigger="cron",
        hour=backup_hour,
        minute=0,
        coalesce=True,
        misfire_grace_time=MISFIRE_GRACE_TIME_SECONDS,
        id="nightly_database_backup",
    )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{now}] Backup scheduler started.")
    print(f"Nightly backup scheduled for {backup_hour:02d}:00 UTC. Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Backup scheduler stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
