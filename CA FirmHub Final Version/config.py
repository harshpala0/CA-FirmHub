"""
config.py — Path & settings resolution for both .exe (frozen) and script mode.

When running as a PyInstaller .exe:
  - BUNDLE_DIR = sys._MEIPASS  → read-only bundled files (static/, firm_identity.json)
  - EXE_DIR    = folder beside the .exe → writable (DB, uploads, exports, booklets)

When running as plain Python:
  - Both point to the script's own directory.
"""
import os, sys, json
from pathlib import Path

# Determine directories
if getattr(sys, 'frozen', False):
    # Compiled .exe mode
    BUNDLE_DIR = Path(os.environ.get('BUNDLE_DIR', sys._MEIPASS))
    BASE_DIR   = Path(os.environ.get('EXE_DIR', os.path.dirname(sys.executable)))
else:
    # Script mode
    BUNDLE_DIR = Path(__file__).resolve().parent
    BASE_DIR   = Path(__file__).resolve().parent

# Writable paths — stored beside the .exe (on the CA firm's machine)
DB_PATH     = BASE_DIR / "audit_management.db"
UPLOAD_DIR  = BASE_DIR / "uploads"
BOOKLET_DIR = BASE_DIR / "booklets"
EXPORT_DIR  = BASE_DIR / "exports"

for d in [UPLOAD_DIR, BOOKLET_DIR, EXPORT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Read-only bundled paths
STATIC_DIR = BUNDLE_DIR / "static"

SECRET_KEY              = os.getenv("SECRET_KEY", "audit-mgmt-secret-change-in-production-2024")
TOKEN_EXPIRE_HOURS      = 8
HOST                    = os.getenv("HOST", "0.0.0.0")
PORT                    = int(os.getenv("PORT", "8000"))
SUBSCRIPTION_TOKEN_HOURS= int(os.getenv("SUBSCRIPTION_TOKEN_HOURS", "720"))  # 30 days

# ── Firm Identity (baked in by admin_generator.py) ────────────
# firm_identity.json is bundled read-only inside the .exe,
# but we also check beside the .exe for dev/override use.
FIRM_NAME    = ""
FIRM_REG_NO  = ""
FIRM_SUB_ID  = ""
FIRM_EXPIRES = None

for _loc in [BASE_DIR / "firm_identity.json", BUNDLE_DIR / "firm_identity.json"]:
    if _loc.exists():
        try:
            _d = json.loads(_loc.read_text(encoding="utf-8"))
            FIRM_NAME    = _d.get("firm_name", "")
            FIRM_REG_NO  = _d.get("firm_reg_no", "")
            FIRM_SUB_ID  = _d.get("sub_id", "")
            FIRM_EXPIRES = _d.get("expires_at")
            break
        except Exception:
            pass
