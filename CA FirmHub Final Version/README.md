# CA FirmHub

A subscription-gated, personalised audit management tool for CA firms.
Distributed as a self-contained `.exe` — **the CA firm installs nothing**.

---

## HOW IT WORKS (Big Picture)

```
YOUR MACHINE                          CA FIRM'S MACHINE
────────────────                      ──────────────────
1. python admin_generator.py          4. Unzip package
   → creates firm package folder      5. Double-click START_HERE.bat
2. python build.bat (inside folder)      → browser opens automatically
   → produces CAFirmHub.exe     6. Enter Subscription ID (once only)
3. Zip dist\CAFirmHub\          7. Log in → work → Sign Out
   → share zip to CA firm                (server stops on sign out)
```

---

## YOUR WORKFLOW (Admin Machine — One-Time Setup)

### Prerequisites (your machine only, not the firm's)
- Python 3.9+ installed
- Run once: `pip install pyinstaller Flask PyJWT Werkzeug python-docx openpyxl waitress`

### Step 1 — Initialise your admin database
```
python main.py        ← runs once to create audit_management.db
Ctrl+C                ← stop it
```

### Step 2 — Generate a personalised package for a CA firm
```
python admin_generator.py   →  Option 1
```
- Enter firm name, reg number, validity
- A folder is created: `generated_packages\AuditMgmt_FirmName_YYYYMMDD\`
- It already contains: `build.bat`, `audit_management.spec`, `launcher.py`

### Step 3 — Build the .exe (inside the firm's folder)
```
cd generated_packages\AuditMgmt_FirmName_YYYYMMDD\
build.bat
```
- Takes 2–5 minutes
- Output: `dist\CAFirmHub\` folder

### Step 4 — Package and share
```
Zip the dist\CAFirmHub\ folder
→ Send the zip to the CA firm
→ Also tell them their Subscription ID (shown after admin_generator.py runs)
```

**That's it. The CA firm receives one zip file.**

---

## CA FIRM WORKFLOW (Zero Installation Required)

1. Receive the zip file from you
2. Unzip it anywhere (Desktop, D: drive, wherever)
3. Double-click **`START_HERE.bat`**
4. Browser opens automatically at `http://127.0.0.1:8000`
5. On first launch: enter the **Subscription ID** you provided → click Activate
6. Log in with credentials → start working
7. When done: click **Sign Out** → server stops → close the black window

**The Subscription ID is asked only once, ever.**
From the second launch onwards: double-click `START_HERE.bat` → log in → done.

### Default Login Credentials (firm should change immediately)
| Role        | Username    | Password  |
|-------------|-------------|-----------|
| Admin       | admin       | admin123  |
| Team Leader | team.leader | audit123  |
| Member      | member1     | audit123  |

---

## RENEWALS

```
python admin_generator.py   →  Option 2
Enter their Subscription ID → extend expiry date
```

- The CA firm does **not** need a new package or new `.exe`
- Their existing data is **never erased**
- On their next login, the renewed expiry is automatically picked up

---

## DATA PRIVACY

- All data (SQLite DB, uploads, booklets, exports) lives **inside the unzipped folder** on the CA firm's machine
- Nothing is sent to your server or any external server
- You cannot access their data — it never leaves their machine
- To back up: they copy the entire unzipped folder to a safe location

---

## PACKAGE FILE STRUCTURE

```
CAFirmHub\                  ← share this entire folder (zipped)
├── START_HERE.bat                ← CA firm double-clicks this
├── CAFirmHub.exe           ← the server (Python + Flask bundled)
├── firm_identity.json            ← firm name, reg no, sub ID, expiry
├── _internal\                    ← bundled Python libraries (do not touch)
│   ├── static\
│   │   └── index.html            ← personalised UI
│   └── ... (Flask, docx, etc.)
├── uploads\                      ← file attachments (created on first run)
├── booklets\                     ← generated audit booklets
└── exports\                      ← query sheet xlsx exports
```

---

## TROUBLESHOOTING

**Windows SmartScreen warning ("Unknown publisher")**
→ Click "More info" → "Run anyway". This is normal for unsigned .exe files.
→ To eliminate permanently: purchase a code signing certificate (~₹8,000/year).

**"Port 8000 is already in use"**
→ Another instance is running. Close it first, or right-click Task Manager → find CAFirmHub.exe → End Task.

**Browser doesn't open automatically**
→ Manually open: http://127.0.0.1:8000

**"Subscription expired" at login**
→ Contact your administrator. They run `admin_generator.py → Option 2` to renew.

**Build takes too long / fails**
→ Ensure all pip packages are installed. Run `build.bat` again — it cleans and rebuilds.
→ Check that `firm_identity.json` exists in the folder before building.

---

## TIPS FOR FASTER/SMALLER .EXE

- Install UPX (free): https://upx.github.io → place `upx.exe` in same folder as `build.bat`
  → Reduces exe size by ~30%
- The `_internal\` folder must stay alongside `CAFirmHub.exe` — they travel together
