#!/usr/bin/env python
"""
List all existing admin users
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/home/batombari/Documents/Full stack dev/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import CustomUser

def list_admins():
    print("=" * 80)
    print("EXISTING ADMIN USERS")
    print("=" * 80)
    
    admins = CustomUser.objects.filter(role='admin')
    
    if not admins.exists():
        print("❌ No admin users found!")
    else:
        print(f"\nFound {admins.count()} admin user(s):\n")
        for admin in admins:
            print(f"  • Username: {admin.username}")
            print(f"    Full Name: {admin.full_name}")
            print(f"    Email: {admin.email or 'Not provided'}")
            print(f"    Phone: {admin.phone_number or 'Not provided'}")
            print(f"    Staff: {admin.is_staff}, Superuser: {admin.is_superuser}")
            print(f"    Active: {admin.is_active}")
            print(f"    Created: {admin.created_at}")
            print("-" * 80)
    
    print("\n" + "=" * 80)
    print("ALL USERS SUMMARY")
    print("=" * 80)
    print(f"Total Users: {CustomUser.objects.count()}")
    print(f"Admins: {CustomUser.objects.filter(role='admin').count()}")
    print(f"Teachers: {CustomUser.objects.filter(role='teacher').count()}")
    print(f"Students: {CustomUser.objects.filter(role='student').count()}")
    print("=" * 80)

if __name__ == '__main__':
    list_admins()
