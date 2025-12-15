from dotenv import load_dotenv
from os import getenv
import sys

load_dotenv()

TRILIUM_URL = getenv("TRILIUM_URL")
TRILIUM_TOKEN = getenv("TRILIUM_TOKEN")
TRILIUM_NOTE_ID = getenv("TRILIUM_NOTE_ID")
TG_BOT_TOKEN = getenv("TG_BOT_TOKEN")
TG_ADMIN_IDS: list[int] = [
    int(id_str) for id_str in (getenv("TG_ADMIN_IDS") or "").split(" ") if id_str
]

REQUIRED_VARS = {
    "TRILIUM_URL": TRILIUM_URL,
    "TRILIUM_TOKEN": TRILIUM_TOKEN,
    "TRILIUM_NOTE_ID": TRILIUM_NOTE_ID,
    "TG_BOT_TOKEN": TG_BOT_TOKEN,
    "TG_ADMIN_IDS": TG_ADMIN_IDS,
}

missing_vars = []

for name, value in REQUIRED_VARS.items():
    if not value:
        missing_vars.append(name)

if missing_vars:
    error_message = (
        f"\n[ERROR] Configuration failed. The application cannot start.\n"
        f"        Missing environment variables: {', '.join(missing_vars)}\n"
    )

    print(error_message, file=sys.stderr)
    sys.exit(1)  # Exit the application with a non-zero status code
