#!/usr/bin/env python
"""
Quick script to create an admin user
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/home/batombari/Documents/Full stack dev/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import CustomUser

def create_admin():
    print("=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60)
    
    # Admin credentials
    username = input("Enter username (numeric only, e.g., 12345): ").strip()
    
    if not username.isdigit():
        print("❌ Error: Username must be numeric!")
        return
    
    # Check if user already exists
    if CustomUser.objects.filter(username=username).exists():
        print(f"❌ Error: User with username {username} already exists!")
        return
    
    full_name = input("Enter full name: ").strip()
    email = input("Enter email (optional, press Enter to skip): ").strip() or None
    phone = input("Enter phone number (optional, press Enter to skip): ").strip() or None
    password = input("Enter password: ").strip()
    
    try:
        # Create admin user
        admin_user = CustomUser.objects.create_user(
            username=username,
            password=password,
            full_name=full_name,
            role='admin',
            email=email,
            phone_number=phone,
            is_staff=True,
            is_superuser=True
        )
        
        print("\n" + "=" * 60)
        print("✅ ADMIN USER CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Username: {admin_user.username}")
        print(f"Full Name: {admin_user.full_name}")
        print(f"Role: {admin_user.role}")
        print(f"Email: {admin_user.email or 'Not provided'}")
        print(f"Phone: {admin_user.phone_number or 'Not provided'}")
        print(f"Is Staff: {admin_user.is_staff}")
        print(f"Is Superuser: {admin_user.is_superuser}")
        print("=" * 60)
        print("\n🎉 You can now login at http://localhost:5173/")
        print(f"   Username: {admin_user.username}")
        print(f"   Password: (the one you entered)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error creating admin user: {str(e)}")

if __name__ == '__main__':
    create_admin()
