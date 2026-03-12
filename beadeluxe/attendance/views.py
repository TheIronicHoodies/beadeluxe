from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from courses.models import CourseUser, Course
from .models import Attendance, AttendanceSession
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now

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
                status = "absent"   # Default value

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
            "role": enrollment.role,
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
def course_attendance_view(request, pk):
    course = Course.objects.get(pk=pk)
    membership = CourseUser.objects.get(user=request.user, course=course)

    if not membership:
        raise PermissionDenied

    # Professor / beadle dashboard
    if membership.role in ["professor", "beadle"]:
        persons = CourseUser.objects.filter(course=course)
        sessions = AttendanceSession.objects.filter(course=course).order_by("date")

        attendance_matrix = []

        for person in persons:
            row = {
                "person": person.user.fullname,
                "course_user_id": person.id,
                "attendance": []
            }

            for session in sessions:
                record = Attendance.objects.filter(
                    session=session,
                    course_user=person
                ).first()

                status = record.status if record else "absent"

                row["attendance"].append({
                    "session_id": session.id,
                    "status": status
                })

            attendance_matrix.append(row)

        context = {
            "course": course,
            "sessions": sessions,
            "attendance_matrix": attendance_matrix
        }

        return render(request, "course_attendance.html", context)

    # Student-only page
    if membership.role == "student":

        sessions = AttendanceSession.objects.filter(
            course=course
        ).order_by("date")

        records = Attendance.objects.filter(course_user=membership)

        record_map = {record.session_id: record for record in records}

        session_rows = []
        cuts = 0

        for session in sessions:

            record = record_map.get(session.id)

            if record:
                status = record.status
            else:
                status = "absent"

            if status == "absent":
                cuts += 1

            if status == "late":
                cuts += 0.5

            session_rows.append({
                "date": session.date,
                "status": status
            })

        total_sessions = len(sessions)

        attendance_percentage = (
            ((total_sessions - cuts) / total_sessions) * 100
            if total_sessions > 0 else 0
        )

        context = {
            "course": course,
            "sessions": session_rows,
            "cuts": cuts,
            "total_sessions": total_sessions,
            "attendance_percentage": round(attendance_percentage, 2)
        }

        return render(request, "course_attendance_student.html", context)
    
@login_required
def update_attendance(request):
    course_user_id = request.POST.get("course_user_id")
    session_id = request.POST.get("session_id")
    status = request.POST.get("status")

    if not course_user_id or not session_id:
        return redirect(request.META.get("HTTP_REFERER"))

    course_user = CourseUser.objects.get(id=course_user_id)
    session = AttendanceSession.objects.get(id=session_id)

    record, created = Attendance.objects.get_or_create(
        course_user=course_user,
        session=session
    )

    record.status = status
    record.save()

    return redirect(request.META.get("HTTP_REFERER"))

@login_required
@require_POST
def add_session(request, course_id):
    course = Course.objects.get(id=course_id)

    membership = CourseUser.objects.filter(
        user=request.user,
        course=course
    ).first()

    if not membership or membership.role not in ["professor", "beadle"]:
        raise PermissionDenied

    date = request.POST.get("session_date")

    AttendanceSession.objects.get_or_create(
        course=course,
        date=date
    )

    return redirect("courses:course_attendance", course_id)

@login_required
@require_POST
def delete_session(request, session_id):
    session = AttendanceSession.objects.get(id=session_id)

    course = session.course

    membership = CourseUser.objects.filter(
        user=request.user,
        course=course
    ).first()

    if not membership or membership.role not in ["professor", "beadle"]:
        raise PermissionDenied

    session.delete()  # cascades attendance deletion

    return redirect("courses:course_attendance", course.id)