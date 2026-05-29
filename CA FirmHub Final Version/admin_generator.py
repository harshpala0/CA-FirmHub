#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         AUDIT MANAGEMENT – ADMIN SUBSCRIPTION GENERATOR      ║
║                         v4 (Personalised)                    ║
╚══════════════════════════════════════════════════════════════╝

Run this script on YOUR (admin) machine to:
  1. Register a new subscription ID in your master database.
  2. Generate a personalised, self-contained folder for the CA firm.
  3. Share the generated folder with the CA firm.

Usage:
    python admin_generator.py
"""

import os, sys, uuid, shutil, json, re
from pathlib import Path
from datetime import datetime, date, timedelta

# ── Paths ─────────────────────────────────────────────────────
BASE     = Path(__file__).resolve().parent
DB_PATH  = BASE / "audit_management.db"
OUT_ROOT = BASE / "generated_packages"

# ── Helpers ───────────────────────────────────────────────────
def prompt(msg, default=None, required=True):
    hint = f" [{default}]" if default is not None and default != "" else ""
    while True:
        val = input(f"  {msg}{hint}: ").strip()
        if not val and default is not None:
            return default
        if val or not required:
            return val
        print("    ✗ This field is required.")

def confirm(msg):
    return input(f"  {msg} (y/n): ").strip().lower() == "y"

def pause(msg="  Press Enter to return to menu..."):
    input(msg)

def banner(title):
    w = 62
    print("\n" + "═"*w)
    print(f"  {title}")
    print("═"*w)

def main_menu():
    print("\n" + "═"*62)
    print("  AUDIT MANAGEMENT – ADMIN SUBSCRIPTION GENERATOR v4")
    print("═"*62)
    print()
    print("  Actions:")
    print("    1) Create new subscription + generate package")
    print("    2) Renew existing subscription")
    print("    3) Deactivate / reactivate a subscription")
    print("    4) List all subscriptions")
    print("    5) Exit")
    print()

# ── Database (admin side) ──────────────────────────────────────
def get_admin_db():
    import sqlite3
    if not DB_PATH.exists():
        print(f"\n  ✗ Admin database not found at:\n      {DB_PATH}")
        print("  Run main.py at least once to initialise the database.\n")
        pause("  Press Enter to exit...")
        sys.exit(1)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def ensure_subscription_columns(db):
    existing = [r[1] for r in db.execute("PRAGMA table_info(subscription_ids)").fetchall()]
    for col, sql in [
        ("firm_name",  "ALTER TABLE subscription_ids ADD COLUMN firm_name TEXT NOT NULL DEFAULT ''"),
        ("firm_reg_no","ALTER TABLE subscription_ids ADD COLUMN firm_reg_no TEXT NOT NULL DEFAULT ''"),
        ("expires_at", "ALTER TABLE subscription_ids ADD COLUMN expires_at TEXT"),
        ("activated",  "ALTER TABLE subscription_ids ADD COLUMN activated INTEGER DEFAULT 0"),
    ]:
        if col not in existing:
            db.execute(sql)
    db.commit()

def register_subscription(db, sub_id, firm_name, firm_reg_no, expires_at, label):
    row = db.execute("SELECT id FROM subscription_ids WHERE sub_id=?", (sub_id,)).fetchone()
    if row:
        print(f"\n  ✗ Subscription ID '{sub_id}' already exists.")
        return False
    db.execute(
        "INSERT INTO subscription_ids (sub_id, label, firm_name, firm_reg_no, is_active, expires_at, activated) "
        "VALUES (?,?,?,?,1,?,0)",
        (sub_id, label or None, firm_name, firm_reg_no, expires_at)
    )
    db.commit()
    print(f"  ✓ Subscription registered in admin database.")
    return True

# ── HTML Personalisation ───────────────────────────────────────
FIRM_PLACEHOLDER_NAME   = "%%FIRM_NAME%%"
FIRM_PLACEHOLDER_REG    = "%%FIRM_REG_NO%%"
FIRM_PLACEHOLDER_SUB_ID = "%%SUBSCRIPTION_ID%%"

def personalise_html(src_html: Path, firm_name: str, firm_reg_no: str, sub_id: str) -> str:
    text = src_html.read_text(encoding="utf-8")
    text = text.replace(FIRM_PLACEHOLDER_NAME, firm_name)
    text = text.replace(FIRM_PLACEHOLDER_REG, firm_reg_no)
    text = text.replace(FIRM_PLACEHOLDER_SUB_ID, sub_id)
    return text

# ── Package Generation ─────────────────────────────────────────
def generate_package(firm_name, firm_reg_no, sub_id, expires_at):
    safe_name = re.sub(r'[^\w\-]', '_', firm_name)[:40]
    pkg_name  = f"AuditMgmt_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    pkg_dir   = OUT_ROOT / pkg_name

    def ignore_fn(src, names):
        ig = set()
        for n in names:
            if n in ("generated_packages", "__pycache__", "dist", "build"):
                ig.add(n)
            if n.endswith(".db") or n.endswith(".pyc"):
                ig.add(n)
        return ig

    shutil.copytree(BASE, pkg_dir, ignore=ignore_fn)

    for d in ["booklets", "exports", "uploads"]:
        (pkg_dir / d).mkdir(exist_ok=True)

    # Personalise index.html
    src_html = pkg_dir / "static" / "index.html"
    if src_html.exists():
        personalised = personalise_html(src_html, firm_name, firm_reg_no, sub_id)
        src_html.write_text(personalised, encoding="utf-8")
        print(f"  ✓ index.html personalised for: {firm_name} ({firm_reg_no})")

    # Write firm_identity.json
    firm_json = {
        "firm_name": firm_name,
        "firm_reg_no": firm_reg_no,
        "sub_id": sub_id,
        "expires_at": expires_at,
        "generated_at": datetime.now().isoformat(),
    }
    (pkg_dir / "firm_identity.json").write_text(json.dumps(firm_json, indent=2), encoding="utf-8")
    print(f"  ✓ firm_identity.json written.")

    # Remove admin_generator from the CA firm's package
    ag = pkg_dir / "admin_generator.py"
    if ag.exists():
        ag.unlink()

    # Include build tools so you can build the exe from within the package
    for build_file in ["build.bat", "audit_management.spec", "launcher.py"]:
        src = BASE / build_file
        if src.exists():
            shutil.copy2(src, pkg_dir / build_file)
    print(f"  ✓ Build tools included (build.bat, spec, launcher.py).")

    return pkg_dir

# ══════════════════════════════════════════════════════════════
#  ACTION HANDLERS
# ══════════════════════════════════════════════════════════════

def action_create(db):
    banner("CREATE NEW SUBSCRIPTION")

    firm_name   = prompt("CA Firm Name (as it should appear on all documents)")
    firm_reg_no = prompt("Firm Registration Number (e.g. 123456W)")
    label       = prompt("Internal label / note (optional)", default="", required=False)

    banner("SUBSCRIPTION VALIDITY")
    print("  How long should this subscription be valid?")
    print("    1) 1 year from today")
    print("    2) 2 years from today")
    print("    3) Custom expiry date")
    print("    4) Unlimited (no expiry)")
    val_choice = prompt("Choice", default="1")

    today = date.today()
    if val_choice == "1":
        expires_at = today.replace(year=today.year + 1).isoformat()
    elif val_choice == "2":
        expires_at = today.replace(year=today.year + 2).isoformat()
    elif val_choice == "3":
        while True:
            raw = prompt("Enter expiry date (YYYY-MM-DD)")
            try:
                expires_at = date.fromisoformat(raw).isoformat()
                break
            except ValueError:
                print("    ✗ Invalid date format. Use YYYY-MM-DD.")
    else:
        expires_at = None

    banner("SUBSCRIPTION ID")
    print("  Generate automatically or enter manually?")
    print("    1) Auto-generate a secure ID (recommended)")
    print("    2) Enter manually")
    id_choice = prompt("Choice", default="1")
    if id_choice == "2":
        while True:
            sub_id = prompt("Enter Subscription ID (min 8 characters)")
            if len(sub_id) >= 8:
                break
            print("    ✗ Must be at least 8 characters.")
    else:
        sub_id = "AMS-" + uuid.uuid4().hex[:16].upper()

    banner("CONFIRM & GENERATE")
    print(f"  Firm Name     : {firm_name}")
    print(f"  Reg Number    : {firm_reg_no}")
    print(f"  Subscription  : {sub_id}")
    print(f"  Valid Until   : {expires_at or 'Unlimited'}")
    print(f"  Label         : {label or '—'}")
    print()

    if not confirm("Confirm and generate package?"):
        print("  Cancelled.")
        pause()
        return

    if not register_subscription(db, sub_id, firm_name, firm_reg_no, expires_at, label):
        pause()
        return

    OUT_ROOT.mkdir(exist_ok=True)
    pkg_dir = generate_package(firm_name, firm_reg_no, sub_id, expires_at)

    banner("DONE ✓")
    print(f"  Package folder created at:")
    print(f"    {pkg_dir}")
    print()
    print(f"  ┌─ SUBSCRIPTION ID (share with CA firm) ─────────────────┐")
    print(f"  │  {sub_id:<55}│")
    print(f"  └────────────────────────────────────────────────────────────┘")
    print()
    print("  Next steps:")
    print("  1. cd into the package folder above")
    print("  2. Run build.bat to produce the .exe")
    print("  3. Zip dist\\CAFirmHub\\ and share with the firm")
    print("  4. Share the Subscription ID above with the firm separately")
    print()
    pause()


def action_renew(db):
    banner("RENEW EXISTING SUBSCRIPTION")
    sub_id = prompt("Enter the Subscription ID to renew")
    row = db.execute("SELECT * FROM subscription_ids WHERE sub_id=?", (sub_id,)).fetchone()
    if not row:
        print(f"\n  ✗ Subscription ID '{sub_id}' not found.")
        pause()
        return

    row = dict(row)
    print(f"\n  Found  : {row['label'] or '(no label)'}")
    print(f"  Firm   : {row['firm_name']} | Reg: {row['firm_reg_no']}")
    print(f"  Expires: {row['expires_at'] or 'Never'}")
    print(f"  Status : {'Active' if row['is_active'] else 'INACTIVE'}")
    print()
    print("  Extend by:")
    print("    1) 1 year")
    print("    2) 2 years")
    print("    3) Custom date")
    choice = prompt("Choice", default="1")

    current_expiry = None
    if row["expires_at"]:
        try:
            current_expiry = date.fromisoformat(row["expires_at"])
        except ValueError:
            pass
    base_date = max(current_expiry, date.today()) if current_expiry else date.today()

    if choice == "1":
        new_expiry = base_date.replace(year=base_date.year + 1)
    elif choice == "2":
        new_expiry = base_date.replace(year=base_date.year + 2)
    else:
        while True:
            raw = prompt("Enter new expiry date (YYYY-MM-DD)")
            try:
                new_expiry = date.fromisoformat(raw)
                break
            except ValueError:
                print("    ✗ Invalid date format. Use YYYY-MM-DD.")

    db.execute(
        "UPDATE subscription_ids SET expires_at=?, is_active=1 WHERE sub_id=?",
        (new_expiry.isoformat(), sub_id)
    )
    db.commit()
    print(f"\n  ✓ Renewed. New expiry: {new_expiry.isoformat()}")
    print("  ℹ  The firm's existing data is untouched.")
    print("  ℹ  No new package needed — the same installation picks this up automatically.")
    pause()


def action_toggle(db):
    banner("DEACTIVATE / REACTIVATE SUBSCRIPTION")
    sub_id = prompt("Enter the Subscription ID")
    row = db.execute("SELECT * FROM subscription_ids WHERE sub_id=?", (sub_id,)).fetchone()
    if not row:
        print(f"\n  ✗ Subscription ID '{sub_id}' not found.")
        pause()
        return

    row = dict(row)
    current = "Active" if row["is_active"] else "INACTIVE"
    new_state = 0 if row["is_active"] else 1
    new_label = "Active" if new_state else "INACTIVE"

    print(f"\n  Firm   : {row['firm_name']} | Reg: {row['firm_reg_no']}")
    print(f"  Current: {current}  →  Will become: {new_label}")
    print()
    if not confirm(f"Confirm {'deactivate' if new_state==0 else 'reactivate'}?"):
        print("  Cancelled.")
        pause()
        return

    db.execute("UPDATE subscription_ids SET is_active=? WHERE sub_id=?", (new_state, sub_id))
    db.commit()
    print(f"\n  ✓ Subscription is now: {new_label}")
    if new_state == 0:
        print("  ℹ  The firm will not be able to log in until reactivated.")
    pause()


def action_list(db):
    banner("ALL SUBSCRIPTIONS")
    rows = db.execute(
        "SELECT * FROM subscription_ids ORDER BY created_at DESC"
    ).fetchall()
    if not rows:
        print("  (none found)")
    else:
        for r in rows:
            r = dict(r)
            status = "ACTIVE  " if r["is_active"] else "INACTIVE"
            exp    = r["expires_at"] or "Never      "
            act    = "✓ Activated" if r["activated"] else "○ Not yet activated"
            print(f"  [{status}] {r['sub_id']}")
            print(f"    Firm    : {r['firm_name']}  |  Reg: {r['firm_reg_no']}")
            print(f"    Label   : {r['label'] or '—'}")
            print(f"    Expires : {exp}  |  {act}")
            print(f"    Uses    : {r['use_count'] or 0}  |  Last used: {r['last_used_at'] or 'Never'}")
            print()
    pause()


# ══════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════

def main():
    while True:
        main_menu()

        action = prompt("Choose action", default="1")

        # Exit early before DB open for option 5
        if action in ("5", "q", "exit", "quit"):
            print("\n  Goodbye.\n")
            sys.exit(0)

        db = get_admin_db()
        ensure_subscription_columns(db)

        try:
            if action == "1":
                action_create(db)
            elif action == "2":
                action_renew(db)
            elif action == "3":
                action_toggle(db)
            elif action == "4":
                action_list(db)
            else:
                print(f"\n  ✗ Invalid choice '{action}'. Please enter 1–5.")
                pause()
        except KeyboardInterrupt:
            print("\n\n  (interrupted — returning to menu)")
        finally:
            db.close()

        # Loop back to menu automatically


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Goodbye.\n")
        sys.exit(0)
