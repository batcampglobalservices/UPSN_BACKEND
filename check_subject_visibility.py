#!/usr/bin/env python
"""
Diagnostic script to check subject visibility for teachers
Run: python backend/check_subject_visibility.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import CustomUser
from classes.models import Subject, Class

def check_teacher_subjects(teacher_username=None):
    """Check what subjects a teacher should see"""
    
    if teacher_username:
        try:
            teacher = CustomUser.objects.get(username=teacher_username, role='teacher')
        except CustomUser.DoesNotExist:
            print(f"❌ Teacher '{teacher_username}' not found")
            return
    else:
        # Get first teacher
        teacher = CustomUser.objects.filter(role='teacher').first()
        if not teacher:
            print("❌ No teachers found in the system")
            return
    
    print(f"\n{'='*60}")
    print(f"Subject Visibility Report for: {teacher.full_name} ({teacher.username})")
    print(f"{'='*60}\n")
    
    # Get teacher's assigned classes
    assigned_classes = Class.objects.filter(assigned_teacher=teacher)
    print(f"📚 Assigned Classes ({assigned_classes.count()}):")
    for cls in assigned_classes:
        print(f"  - {cls.name} ({cls.level})")
    print()
    
    # Get subjects they directly teach
    direct_subjects = Subject.objects.filter(assigned_teacher=teacher).select_related('assigned_class')
    print(f"📝 Subjects Directly Teaching ({direct_subjects.count()}):")
    for subj in direct_subjects:
        print(f"  - {subj.name} ({subj.code}) in {subj.assigned_class.name}")
    print()
    
    # Get subjects in their assigned classes (taught by others)
    class_subjects = Subject.objects.filter(
        assigned_class__assigned_teacher=teacher
    ).exclude(
        assigned_teacher=teacher
    ).select_related('assigned_class', 'assigned_teacher')
    
    print(f"📖 Subjects in Assigned Classes (taught by others) ({class_subjects.count()}):")
    for subj in class_subjects:
        teacher_name = subj.assigned_teacher.full_name if subj.assigned_teacher else "Not assigned"
        print(f"  - {subj.name} ({subj.code}) in {subj.assigned_class.name} [Teacher: {teacher_name}]")
    print()
    
    # Total visible subjects (what the API returns)
    from django.db.models import Q
    total_visible = Subject.objects.filter(
        Q(assigned_teacher=teacher) | 
        Q(assigned_class__assigned_teacher=teacher)
    ).distinct().select_related('assigned_class', 'assigned_teacher')
    
    print(f"✅ TOTAL VISIBLE SUBJECTS ({total_visible.count()}):")
    for subj in total_visible:
        teacher_name = subj.assigned_teacher.full_name if subj.assigned_teacher else "Not assigned"
        reason = "Direct" if subj.assigned_teacher == teacher else "Class Teacher"
        print(f"  - {subj.name} ({subj.code}) in {subj.assigned_class.name} [{reason}] [Teacher: {teacher_name}]")
    print()
    
    # All subjects in the system (for comparison)
    all_subjects = Subject.objects.all()
    print(f"📊 Total Subjects in System: {all_subjects.count()}")
    print(f"📊 Visible to {teacher.username}: {total_visible.count()}")
    print(f"📊 Not Visible: {all_subjects.count() - total_visible.count()}")
    print()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Check subject visibility for teachers')
    parser.add_argument('--teacher', '-t', help='Teacher username to check', default=None)
    parser.add_argument('--all', '-a', action='store_true', help='Check all teachers')
    
    args = parser.parse_args()
    
    if args.all:
        teachers = CustomUser.objects.filter(role='teacher')
        print(f"\n🔍 Checking {teachers.count()} teachers...\n")
        for teacher in teachers:
            check_teacher_subjects(teacher.username)
            print()
    else:
        check_teacher_subjects(args.teacher)
