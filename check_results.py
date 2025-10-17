#!/usr/bin/env python
"""
Quick diagnostic script to check result data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import User
from results.models import Result, ResultSummary, AcademicSession

print("=" * 60)
print("RESULT SYSTEM DIAGNOSTIC")
print("=" * 60)

# Check students
students = User.objects.filter(role='student')
print(f"\n📊 Total Students: {students.count()}")
if students.exists():
    print("\nStudent List:")
    for student in students[:5]:  # Show first 5
        print(f"  - ID: {student.id}, Username: {student.username}, Name: {student.full_name}")

# Check academic sessions
sessions = AcademicSession.objects.all()
print(f"\n📅 Total Sessions: {sessions.count()}")
if sessions.exists():
    print("\nSession List:")
    for session in sessions:
        status = "✅ ACTIVE" if session.is_active else "❌ Inactive"
        release = f"Release: {session.result_release_date}" if session.result_release_date else "No release date"
        print(f"  - {status} | {session.name} | {release}")

# Check results
results = Result.objects.all()
print(f"\n📝 Total Results: {results.count()}")
if results.exists():
    print("\nResult Breakdown by Student:")
    for student in students[:5]:  # First 5 students
        student_results = Result.objects.filter(student=student)
        print(f"  - {student.full_name} ({student.username}): {student_results.count()} results")
        if student_results.exists():
            for result in student_results[:3]:  # First 3 results
                print(f"      * {result.subject.name}: Test={result.test_score}, Exam={result.exam_score}, Total={result.total}, Grade={result.grade}")

# Check summaries
summaries = ResultSummary.objects.all()
print(f"\n📊 Total Result Summaries: {summaries.count()}")
if summaries.exists():
    print("\nSummary Breakdown:")
    for summary in summaries[:5]:
        print(f"  - {summary.student.full_name}: {summary.session.name} - {summary.term}")
        print(f"      Subjects: {summary.total_subjects}, Avg: {summary.average_score:.2f}%, Grade: {summary.overall_grade}")

# Specific test: Check first student
if students.exists():
    test_student = students.first()
    print(f"\n🔍 DETAILED TEST FOR: {test_student.full_name} (ID: {test_student.id})")
    print(f"   Role: {test_student.role}")
    print(f"   Username: {test_student.username}")
    
    test_results = Result.objects.filter(student=test_student)
    print(f"   Results count: {test_results.count()}")
    
    if test_results.exists():
        print(f"   Sample result:")
        r = test_results.first()
        print(f"      - Subject: {r.subject.name}")
        print(f"      - Session: {r.session.name}")
        print(f"      - Term: {r.term}")
        print(f"      - Scores: Test={r.test_score}, Exam={r.exam_score}, Total={r.total}")
        print(f"      - Grade: {r.grade}")
    else:
        print("   ⚠️ NO RESULTS FOUND FOR THIS STUDENT")
    
    test_summaries = ResultSummary.objects.filter(student=test_student)
    print(f"   Summaries count: {test_summaries.count()}")
    if not test_summaries.exists():
        print("   ⚠️ NO SUMMARIES FOUND FOR THIS STUDENT")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

# Recommendations
print("\n💡 RECOMMENDATIONS:")
if not students.exists():
    print("  ❌ No students found. Create student accounts first.")
elif not results.exists():
    print("  ❌ No results found. Upload scores using Score Entry.")
elif not summaries.exists():
    print("  ❌ No summaries found. Summaries should auto-generate when results are saved.")
    print("     Try creating a result or run: python manage.py shell")
    print("     >>> from results.models import ResultSummary")
    print("     >>> ResultSummary.objects.all().delete()  # Clear old ones")
    print("     >>> # Then re-save a result to trigger auto-generation")
else:
    print("  ✅ Data looks good! Check the frontend console logs for API issues.")
