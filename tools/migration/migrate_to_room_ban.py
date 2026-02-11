#!/usr/bin/env python3
# Migration script to create RoomBan table and convert existing Member.role='banned' to RoomBan records

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import RoomBan, Member
from datetime import datetime

def migrate():
    app = create_app()
    
    with app.app_context():
        print("[MIGRATION] Starting RoomBan migration...")
        
        # Create RoomBan table if it doesn't exist
        try:
            db.create_all()
            print("[MIGRATION] ✓ RoomBan table created/verified")
        except Exception as e:
            print(f"[MIGRATION] ✗ Error creating table: {e}")
            return
        
        # Convert existing Member.role='banned' to RoomBan records
        banned_members = Member.query.filter_by(role='banned').all()
        
        if banned_members:
            print(f"[MIGRATION] Found {len(banned_members)} banned Member records")
            
            for member in banned_members:
                # Check if RoomBan record already exists
                existing_ban = RoomBan.query.filter_by(
                    user_id=member.user_id,
                    room_id=member.room_id
                ).first()
                
                if not existing_ban:
                    # Create RoomBan record
                    room_ban = RoomBan(
                        room_id=member.room_id,
                        user_id=member.user_id,
                        reason='Converted from Member.role=banned',
                        banned_at=datetime.utcnow()
                    )
                    db.session.add(room_ban)
                    print(f"[MIGRATION] Created RoomBan for user {member.user_id} in room {member.room_id}")
                
                # Delete the Member record
                db.session.delete(member)
                print(f"[MIGRATION] Deleted Member record for user {member.user_id} in room {member.room_id}")
            
            db.session.commit()
            print(f"[MIGRATION] ✓ Migrated {len(banned_members)} banned members")
        else:
            print("[MIGRATION] No banned Member records found")
        
        print("[MIGRATION] ✓ Migration complete!")

if __name__ == '__main__':
    migrate()
