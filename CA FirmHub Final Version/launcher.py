"""
launcher.py — PyInstaller entry point for CA FirmHub.

Fixes all paths for frozen (.exe) mode, then runs main.py properly.
"""
import sys
import os

# ── 1. Resolve directories ────────────────────────────────────
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    BUNDLE_DIR = sys._MEIPASS                          # read-only bundled files
    EXE_DIR    = os.path.dirname(sys.executable)       # writable folder beside .exe
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR    = BUNDLE_DIR

# ── 2. Working directory = beside the .exe ────────────────────
# SQLite DB, uploads, booklets, exports all live here (user's machine)
os.chdir(EXE_DIR)

# ── 3. Tell config.py where everything is ─────────────────────
os.environ['BUNDLE_DIR'] = BUNDLE_DIR
os.environ['EXE_DIR']    = EXE_DIR

# ── 4. Ensure bundled packages are on the path ───────────────
if BUNDLE_DIR not in sys.path:
    sys.path.insert(0, BUNDLE_DIR)

# ── 5. Run main.py as __main__ (correct way via runpy) ────────
# This triggers the if __name__ == '__main__' block properly.
import runpy
runpy.run_path(
    os.path.join(BUNDLE_DIR, 'main.py'),
    run_name='__main__'
)
