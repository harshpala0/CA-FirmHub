"""
CA FirmHub - Vercel Production Build Script
Initializes database and prepares for deployment
"""
import os
import sys
from pathlib import Path

print("=" * 60)
print("  CA FIRMHUB - VERCEL BUILD")
print("=" * 60)

try:
    # Import and initialize database
    print("\n📦 Initializing database...")
    from database import init_db, get_db, init_subscriptions_table, init_v5_tables
    from seed_data import seed
    
    # Initialize database schema
    init_db()
    print("   ✅ Database schema created")
    
    # Create subscriptions table
    db = get_db()
    init_subscriptions_table(db)
    print("   ✅ Subscriptions table initialized")
    
    # Initialize v5 tables
    init_v5_tables(db)
    print("   ✅ V5 tables initialized")
    
    # Seed default data
    seed(db)
    print("   ✅ Seed data loaded")
    
    db.close()
    print("\n✅ Build completed successfully!")
    
except Exception as e:
    print(f"\n⚠️  Build warning: {e}")
    print("   (App will initialize on first request)")
    sys.exit(0)  # Don't fail the build

print("\n" + "=" * 60)
print("  Ready for deployment! 🚀")
print("=" * 60)
