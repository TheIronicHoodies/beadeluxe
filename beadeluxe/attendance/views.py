from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import CourseUser, Course
from .models import Attendance, AttendanceSession
from django.core.exceptions import PermissionDenied

# Create your views here.

@login_required
def attendance_view(request):

    user = request.user

    # Get all courses enrolled for this user
    enrollments = CourseUser.objects.filter(user=user)

    attendance_data = []

    for enrollment in enrollments:
        records = Attendance.objects.filter(course_user=enrollment)

        total_classes = records.count()

        cuts = records.filter(status="absent").count()
        lates = records.filter(status="late").count()

        # Make lates count as half-cut
        cuts = cuts + (lates * 0.5)

        attendance_data.append({
            "course": enrollment.course,
            "records": records,
            "cuts": cuts,
            "total_classes": total_classes
        })

    context = {
        "attendance_data": attendance_data
    }

    return render(request, "attendance.html", context)

@login_required
def course_attendance_view(request, course_id):

    course = Course.objects.get(id=course_id)

    # Check if user is professor or beadle for the course
    membership = CourseUser.objects.filter(
        user=request.user,
        course=course
    ).first()

    if not membership or membership.role not in ["professor", "beadle"]:
        return render(request, "403.html")

    students = CourseUser.objects.filter(
        course=course,
        role="student"
    )

    sessions = AttendanceSession.objects.filter(course=course).order_by("date")

    attendance_table = []

    for student in students:

        records = Attendance.objects.filter(course_user=student)

        total_classes = records.count()
        cuts = records.filter(status="absent").count()

        attendance_table.append({
            "student": student.user.fullname,
            "records": records,
            "cuts": cuts,
            "total": total_classes
        })

    context = {
        "course": course,
        "sessions": sessions,
        "attendance_table": attendance_table
    }

    return render(request, "course_attendance.html", context)