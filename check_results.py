#!/usr/bin/env python
"""
Quick diagnostic script to check result data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import CustomUser
from results.models import Result, ResultSummary, AcademicSession

print("=" * 60)
print("RESULT SYSTEM DIAGNOSTIC")
print("=" * 60)

# Check pupils
pupils = CustomUser.objects.filter(role='pupil')
print(f"\n📊 Total Pupils: {pupils.count()}")
if pupils.exists():
    print("\nPupil List:")
    for pupil in pupils[:5]:  # Show first 5
        print(f"  - ID: {pupil.id}, Username: {pupil.username}, Name: {pupil.full_name}")

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
    print("\nResult Breakdown by Pupil:")
    for pupil in pupils[:5]:  # First 5 pupils
        pupil_results = Result.objects.filter(pupil=pupil)
        print(f"  - {pupil.full_name} ({pupil.username}): {pupil_results.count()} results")
        if pupil_results.exists():
            for result in pupil_results[:3]:  # First 3 results
                print(f"      * {result.subject.name}: Test={result.test_score}, Exam={result.exam_score}, Total={result.total}, Grade={result.grade}")

# Check summaries
summaries = ResultSummary.objects.all()
print(f"\n📊 Total Result Summaries: {summaries.count()}")
if summaries.exists():
    print("\nSummary Breakdown:")
    for summary in summaries[:5]:
        print(f"  - {summary.pupil.full_name}: {summary.session.name} - {summary.term}")
        print(f"      Subjects: {summary.total_subjects}, Avg: {summary.average_score:.2f}%, Grade: {summary.overall_grade}")

# Specific test: Check first pupil
if pupils.exists():
    test_pupil = pupils.first()
    print(f"\n🔍 DETAILED TEST FOR: {test_pupil.full_name} (ID: {test_pupil.id})")
    print(f"   Role: {test_pupil.role}")
    print(f"   Username: {test_pupil.username}")
    
    test_results = Result.objects.filter(pupil=test_pupil)
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
        print("   ⚠️ NO RESULTS FOUND FOR THIS PUPIL")
    
    test_summaries = ResultSummary.objects.filter(pupil=test_pupil)
    print(f"   Summaries count: {test_summaries.count()}")
    if not test_summaries.exists():
        print("   ⚠️ NO SUMMARIES FOUND FOR THIS PUPIL")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

# Recommendations
print("\n💡 RECOMMENDATIONS:")
if not pupils.exists():
    print("  ❌ No pupils found. Create pupil accounts first.")
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
