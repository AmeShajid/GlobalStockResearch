"""Phase 1.1 verification: confirm the Reddit app credentials load from .env.

What it does:
  1. Loads REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET from backend/.env
     (never hardcoded — read via python-dotenv / os.environ).
  2. Confirms both are present and are not the template placeholders.
  3. Prints "reddit credentials ok" on success.

This does NOT make a live Reddit API call — PRAW is installed in Phase 1.2 and
the first real API call belongs to the collector in Phase 1.6. This script only
checks that the credentials are wired up correctly.

Run from the backend folder with the venv active:
    python check_reddit_credentials.py
"""

from pathlib import Path
import os
import sys

from dotenv import load_dotenv


# Paths are relative to this file, never hardcoded to C:\Users\...
BACKEND_DIR = Path(__file__).resolve().parent
ENV_FILE = BACKEND_DIR / ".env"

# The placeholder values shipped in .env / .env.example. If either variable
# still holds its placeholder, the real credentials have not been filled in.
PLACEHOLDERS = {
    "REDDIT_CLIENT_ID": "your-reddit-client-id-here",
    "REDDIT_CLIENT_SECRET": "your-reddit-client-secret-here",
}


def main() -> int:
    load_dotenv(ENV_FILE)

    missing = []
    for name, placeholder in PLACEHOLDERS.items():
        value = os.environ.get(name)
        if not value or value == placeholder:
            missing.append(name)

    if missing:
        print(
            "setup incomplete: the following Reddit credentials are not set in "
            f"{ENV_FILE}: {', '.join(missing)}.\n"
            "Create a 'script' app at https://www.reddit.com/prefs/apps and put "
            "the real Client ID and Client Secret in .env (see .env.example)."
        )
        return 1

    print("reddit credentials ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
