#!/usr/bin/env python
"""
Script to update old 'student' role to 'pupil' role
This is needed after the terminology migration.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import CustomUser

def update_student_roles():
    """Update all users with role='student' to role='pupil'"""
    print("=" * 60)
    print("UPDATING OLD 'student' ROLES TO 'pupil'")
    print("=" * 60)
    
    # Find all users with old 'student' role
    old_students = CustomUser.objects.filter(role='student')
    count = old_students.count()
    
    print(f"\nFound {count} user(s) with old 'student' role:\n")
    
    for user in old_students:
        print(f"  - ID: {user.id} | Username: {user.username} | Name: {user.full_name or '(empty)'}")
    
    if count == 0:
        print("\n✅ No users need updating. All roles are correct!")
        return 0
    
    # Update them
    print(f"\n📝 Updating {count} user(s) to 'pupil' role...")
    updated = old_students.update(role='pupil')
    
    print(f"\n✅ Successfully updated {updated} user(s)!")
    print("\nVerifying update...")
    
    # Verify
    remaining = CustomUser.objects.filter(role='student').count()
    if remaining == 0:
        print("✅ Verification passed! No 'student' roles remaining.")
    else:
        print(f"⚠️  Warning: {remaining} 'student' roles still exist!")
    
    return updated

if __name__ == '__main__':
    print("\n🔄 ROLE MIGRATION SCRIPT")
    print("This script updates old 'student' roles to 'pupil' roles.\n")
    
    updated_count = update_student_roles()
    
    if updated_count > 0:
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE!")
        print("=" * 60)
        print(f"\n✅ {updated_count} user(s) updated from 'student' to 'pupil'")
        print("\nYou can now:")
        print("1. Refresh the Score Entry page")
        print("2. Try entering results again")
        print("3. All pupils should now be visible and saveable!")
    
    print("\n" + "=" * 60 + "\n")
