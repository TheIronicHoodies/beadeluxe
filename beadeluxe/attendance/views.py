from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import CourseUser, Course
from .models import Attendance, AttendanceSession
from django.core.exceptions import PermissionDenied

# Create your views here.

@login_required
def attendance_view(request):

    user = request.user

    # Get all course memberships for the user
    enrollments = CourseUser.objects.filter(
        user=user
    )

    attendance_data = []

    for enrollment in enrollments:

        sessions = AttendanceSession.objects.filter(
            course=enrollment.course
        ).order_by("date")

        records = Attendance.objects.filter(
            course_user=enrollment
        )

        record_map = {
            record.session_id: record
            for record in records
        }

        session_rows = []

        cuts = 0

        for session in sessions:

            record = record_map.get(session.id)

            if record:
                status = record.status
            else:
                status = "absent"   # default

            if status == "absent":
                cuts += 1

            session_rows.append({
                "date": session.date,
                "status": status
            })

        total_sessions = len(sessions)

        if total_sessions > 0:
            attendance_percentage = ((total_sessions - cuts) / total_sessions) * 100
        else:
            attendance_percentage = 0

        attendance_data.append({
            "course": enrollment.course,
            "role": enrollment.role,   # useful for display
            "sessions": session_rows,
            "total_sessions": total_sessions,
            "cuts": cuts,
            "attendance_percentage": round(attendance_percentage, 2)
        })

    return render(
        request,
        "attendance.html",
        {"attendance_data": attendance_data}
    )

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

    persons = CourseUser.objects.filter(
        course=course,
    )

    sessions = AttendanceSession.objects.filter(
        course=course
    ).order_by("date")

    attendance_matrix = []

    for person in persons:
        row = {
            "person": person.user.fullname,
            "attendance": []
        }

        for session in sessions:
            record = Attendance.objects.filter(
                session=session,
                course_user=person
            ).first()

            if record:
                row["attendance"].append(record.status)
            else:
                row["attendance"].append("absent")      # Default value

        attendance_matrix.append(row)

    context = {
        "course": course,
        "sessions": sessions,
        "attendance_matrix": attendance_matrix
    }

    return render(request, "course_attendance.html", context)