"""
Vercel API Entry Point
Serverless handler for Flask application
"""
import sys
import os
from pathlib import Path

# Add CA FirmHub to path
ca_path = Path(__file__).parent.parent / "CA FirmHub Final Version"
sys.path.insert(0, str(ca_path))

# Set production environment
os.environ.setdefault("FLASK_ENV", "production")

# Initialize database on first import
try:
    from database import init_db, get_db, init_subscriptions_table, init_v5_tables
    from seed_data import seed
    
    init_db()
    db = get_db()
    init_subscriptions_table(db)
    init_v5_tables(db)
    seed(db)
    db.close()
except Exception as e:
    print(f"Database init warning: {e}")

# Import and export Flask app for Vercel
from main import app

# Ensure app is properly configured
app.config['JSON_SORT_KEYS'] = False

# This is required by Vercel - it looks for 'app'
__all__ = ['app']
