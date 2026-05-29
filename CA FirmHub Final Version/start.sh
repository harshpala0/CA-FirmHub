#!/bin/bash
# ===============================================
#  AUDIT MANAGEMENT SYSTEM v4 - Linux/Mac Launcher
#  Run: bash start.sh
# ===============================================
cd "$(dirname "$0")"

echo ""
echo "  ============================================"
echo "    AUDIT MANAGEMENT SYSTEM v4 - Setup"
echo "  ============================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "  [ERROR] python3 not found. Install Python 3.9+ first."
    exit 1
fi
echo "  [OK] Python found: $(python3 --version)"

# Install dependencies
echo "  [SETUP] Checking required libraries..."
python3 -m pip install -q Flask PyJWT Werkzeug python-docx openpyxl waitress 2>/dev/null || \
python3 -m pip install Flask PyJWT Werkzeug python-docx openpyxl 2>/dev/null
echo "  [OK] Libraries ready"

# Create directories
mkdir -p uploads booklets exports

echo ""
echo "  ============================================"
echo "    Starting CA FirmHub Server..."
echo "  ============================================"
echo ""
echo "  Browser will open automatically."
echo "  If not, open: http://127.0.0.1:8000"
echo ""
echo "  IMPORTANT: The server stops automatically"
echo "  when you Sign Out from the application."
echo "  Press Ctrl+C to force stop if needed."
echo ""

python3 main.py

echo ""
echo "  ============================================"
echo "    Server has stopped. Safe to close."
echo "  ============================================"
echo ""
