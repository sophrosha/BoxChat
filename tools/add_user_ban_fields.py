#!/usr/bin/env python3

# Migration: Add user ban fields to User table
# is_banned: Boolean flag for global ban status
# banned_ips: Comma-separated list of banned IP addresses
# ban_reason: Reason for the ban
# banned_at: Timestamp when user was banned

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def run_migration():
    # Add ban-related columns to User table
    app = create_app()
    
    with app.app_context():
        # Get database connection
        connection = db.engine.connect()
        
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('user')]
            
            # Add columns if they don't exist
            if 'is_banned' not in columns:
                connection.execute(text("ALTER TABLE user ADD COLUMN is_banned BOOLEAN DEFAULT False"))
                print("Added is_banned column")
            
            if 'banned_ips' not in columns:
                connection.execute(text("ALTER TABLE user ADD COLUMN banned_ips TEXT DEFAULT ''"))
                print("Added banned_ips column")
            
            if 'ban_reason' not in columns:
                connection.execute(text("ALTER TABLE user ADD COLUMN ban_reason VARCHAR(500)"))
                print("Added ban_reason column")
            
            if 'banned_at' not in columns:
                connection.execute(text("ALTER TABLE user ADD COLUMN banned_at DATETIME"))
                print("Added banned_at column")
            
            connection.commit()
            print("\n✓ Migration completed successfully!")
            
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()

if __name__ == '__main__':
    run_migration()
