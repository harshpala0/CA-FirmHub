"""\nVercel API Entry Point\nServerless handler for Flask application\n"""
import sys
import os
from pathlib import Path

# Add CA FirmHub to path
ca_path = Path(__file__).parent.parent / "CA FirmHub Final Version"
sys.path.insert(0, str(ca_path))

# Set production environment
os.environ.setdefault("FLASK_ENV", "production")

# Import Flask app
try:
    from main import app
    app.config['JSON_SORT_KEYS'] = False
except ImportError as e:
    print(f"❌ Failed to import app: {e}")
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return jsonify({"error": str(e), "status": "failed"}), 500