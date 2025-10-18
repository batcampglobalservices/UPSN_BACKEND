#!/usr/bin/env python
"""
Script to check for orphaned pupil profiles (profiles without valid user accounts)
and optionally fix the data integrity issues.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import CustomUser, PupilProfile

def check_orphaned_pupils():
    """Check for pupil profiles without valid user accounts"""
    print("=" * 60)
    print("CHECKING FOR ORPHANED PUPIL PROFILES")
    print("=" * 60)
    
    all_pupils = PupilProfile.objects.all()
    print(f"\nTotal PupilProfiles in database: {all_pupils.count()}")
    
    # Check for profiles with null or invalid user references
    orphaned = []
    for pupil in all_pupils:
        try:
            if not pupil.user:
                orphaned.append(pupil)
                print(f"\n❌ ORPHANED: PupilProfile ID {pupil.id}")
                print(f"   - Admission: {pupil.admission_number}")
                print(f"   - Class: {pupil.pupil_class}")
                print(f"   - User: None (NULL reference)")
            elif not CustomUser.objects.filter(id=pupil.user.id).exists():
                orphaned.append(pupil)
                print(f"\n❌ ORPHANED: PupilProfile ID {pupil.id}")
                print(f"   - Admission: {pupil.admission_number}")
                print(f"   - Class: {pupil.pupil_class}")
                print(f"   - User ID: {pupil.user.id} (DOES NOT EXIST)")
        except Exception as e:
            orphaned.append(pupil)
            print(f"\n❌ ERROR checking PupilProfile ID {pupil.id}: {e}")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: Found {len(orphaned)} orphaned pupil profile(s)")
    print("=" * 60)
    
    if orphaned:
        print("\n⚠️  These pupil profiles cannot have results entered for them.")
        print("Options:")
        print("1. Delete the orphaned profiles")
        print("2. Create user accounts for them")
        print("3. Leave them as-is")
        
        return orphaned
    else:
        print("\n✅ All pupil profiles have valid user accounts!")
        return []

def list_all_users():
    """List all users in the system"""
    print("\n" + "=" * 60)
    print("ALL USERS IN SYSTEM")
    print("=" * 60)
    
    users = CustomUser.objects.all().order_by('id')
    print(f"\nTotal users: {users.count()}\n")
    
    for user in users:
        print(f"ID: {user.id:3d} | Role: {user.role:7s} | Username: {user.username:20s} | Name: {user.full_name}")
    
    print("\n" + "=" * 60)

def delete_orphaned_pupils(orphaned_pupils):
    """Delete orphaned pupil profiles"""
    if not orphaned_pupils:
        print("\n✅ No orphaned pupils to delete.")
        return
    
    print("\n" + "=" * 60)
    print("DELETING ORPHANED PUPIL PROFILES")
    print("=" * 60)
    
    for pupil in orphaned_pupils:
        try:
            admission = pupil.admission_number
            pupil_id = pupil.id
            pupil.delete()
            print(f"✅ Deleted PupilProfile ID {pupil_id} (Admission: {admission})")
        except Exception as e:
            print(f"❌ Error deleting PupilProfile ID {pupil.id}: {e}")
    
    print(f"\n✅ Cleanup complete! Deleted {len(orphaned_pupils)} orphaned profile(s).")

if __name__ == '__main__':
    print("\n🔍 PUPIL PROFILE INTEGRITY CHECK")
    print("This script checks for pupil profiles without valid user accounts.\n")
    
    # Check for orphaned pupils
    orphaned = check_orphaned_pupils()
    
    # List all users for reference
    list_all_users()
    
    # Ask if user wants to delete orphaned profiles
    if orphaned:
        print("\n" + "=" * 60)
        response = input("\nDo you want to DELETE these orphaned pupil profiles? (yes/no): ").strip().lower()
        if response == 'yes':
            delete_orphaned_pupils(orphaned)
            print("\n✅ Database cleaned! Orphaned profiles removed.")
        else:
            print("\n⚠️  Orphaned profiles remain in database.")
            print("You can:")
            print("1. Create user accounts for them in the admin panel")
            print("2. Run this script again to delete them")
    
    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60 + "\n")
