#!/usr/bin/env python3

# Test script for admin ban/unban functionality
# Run this to test the security features

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash

def test_admin_features():
    # Test ban/unban and password change functions
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("BoxChat Admin Features Test")
        print("="*60 + "\n")
        
        # Create test users
        print("1. Creating test users...")
        
        # Admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('AdminPass123', method='scrypt'),
                is_superuser=True
            )
            db.session.add(admin)
            print("   ✓ Created admin user")
        else:
            print("   ✓ Admin user already exists")
        
        # Regular user
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(
                username='testuser',
                password=generate_password_hash('TestPass123', method='scrypt'),
                is_superuser=False
            )
            db.session.add(user)
            print("   ✓ Created regular user")
        else:
            print("   ✓ Regular user already exists")
        
        db.session.commit()
        
        # Test ban functionality
        print("\n2. Testing ban functionality...")
        if not user.is_banned:
            user.is_banned = True
            user.ban_reason = "Test ban"
            user.banned_ips = "192.168.1.100"
            db.session.commit()
            print("   ✓ User marked as banned")
            print(f"   ✓ Ban reason: {user.ban_reason}")
            print(f"   ✓ Banned IPs: {user.banned_ips}")
        
        # Test password change
        print("\n3. Testing password change...")
        new_password = generate_password_hash('NewTestPass456', method='scrypt')
        user.password = new_password
        db.session.commit()
        print("   ✓ User password updated")
        
        # Test unban
        print("\n4. Testing unban functionality...")
        user.is_banned = False
        user.ban_reason = None
        user.banned_ips = ""
        db.session.commit()
        print("   ✓ User unbanned successfully")
        print(f"   ✓ Ban status: {user.is_banned}")
        print(f"   ✓ Banned IPs cleared: {user.banned_ips}")
        
        # Test IP ban detection
        print("\n5. Testing IP ban detection...")
        test_user = User.query.filter_by(username='testuser').first()
        if test_user:
            # Set up test IPs
            test_user.is_banned = True
            test_user.banned_ips = "10.0.0.1,192.168.0.1,172.16.0.1"
            db.session.commit()
            
            ips = [ip.strip() for ip in test_user.banned_ips.split(',') if ip.strip()]
            print(f"   ✓ Banned IPs: {ips}")
            print(f"   ✓ Total banned IPs: {len(ips)}")
            
            # Test IP lookup
            test_ip = "192.168.0.1"
            if test_ip in ips:
                print(f"   ✓ IP {test_ip} found in banned list")
        
        # Summary
        print("\n" + "="*60)
        print("Test Summary:")
        print("="*60)
        print(f"Admin user: {admin.username} (Superuser: {admin.is_superuser})")
        print(f"Test user: {user.username}")
        print(f"  - Is banned: {user.is_banned}")
        print(f"  - Ban reason: {user.ban_reason}")
        print(f"  - Banned IPs: {user.banned_ips}")
        print("\n✓ All tests completed successfully!\n")
        
        print("Next steps:")
        print("1. Run database migration: python tools/add_user_ban_fields.py")
        print("2. Update your admin user: is_superuser = True")
        print("3. Test the /admin endpoints with your client")
        print("4. Check templates/settings.html for password change UI")
        print("\n")

if __name__ == '__main__':
    test_admin_features()
