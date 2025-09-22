#!/usr/bin/env python3
# reset_db.py - Reset database để tạo lại tables

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine
from sqlalchemy import text

def reset_database():
    print("🔍 Resetting database...")
    
    try:
        with engine.connect() as conn:
            # Drop existing tables
            conn.execute(text('DROP TABLE IF EXISTS chat_messages'))
            conn.execute(text('DROP TABLE IF EXISTS chats'))
            conn.execute(text('DROP TABLE IF EXISTS chat_sessions'))
            conn.commit()
            
        print("✅ Dropped existing chat tables")
        
        # Run migration from beginning
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'alembic', 'upgrade', 'head'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database migration successful")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        return False

if __name__ == "__main__":
    success = reset_database()
    if success:
        print("🎉 Database reset completed successfully!")
    else:
        print("❌ Database reset failed!")
        sys.exit(1)
