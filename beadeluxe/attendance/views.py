from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST

from courses.models import CourseUser, Course
from .models import Attendance, AttendanceSession

from django.core.exceptions import PermissionDenied

# Create your views here.

# displays a single user's attendance for all their classes
class AttendanceView(LoginRequiredMixin, View):
    def get(self, request):

        # get the logged in user's courseuser object
        enrollments = CourseUser.objects.filter(user=request.user)
        attendance_data = []

        # display attendance for each course the user is enrolled in
        for enrollment in enrollments:
            sessions = AttendanceSession.objects.filter(
                course=enrollment.course
            ).order_by("date")

            # get attendance records
            records = Attendance.objects.filter(course_user=enrollment)
            record_map = {r.session_id: r for r in records}

            # so far, no sessions, cuts are 0 by default
            session_rows = []
            cuts = 0

            # per class, check when they were absent
            for session in sessions:
                record = record_map.get(session.id)
                status = record.status if record else "absent"

                if status == "absent":
                    cuts += 1

                session_rows.append({
                    "date": session.date,
                    "status": status
                })

            # total is the number of sessions
            total = len(sessions)
            percent = ((total - cuts) / total * 100) if total > 0 else 0

            attendance_data.append({
                "course": enrollment.course,
                "role": enrollment.role,
                "sessions": session_rows,
                "total_sessions": total,
                "cuts": cuts,
                "attendance_percentage": round(percent, 2)
            })

        return render(request, "attendance.html", {
            "attendance_data": attendance_data
        })

# displays a course's attendance sheet
class CourseAttendanceView(LoginRequiredMixin, View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership:
            raise PermissionDenied

        # PROFESSOR or BEADLE
        if membership.role in ["professor", "beadle"]:
            return self.professor_view(request, course)

        # STUDENT
        return self.student_view(request, course, membership)

    # for professors and beadles
    def professor_view(self, request, course):
        role_filter = request.GET.get("role")

        persons = CourseUser.objects.filter(course=course)

        if role_filter in ["student", "professor", "beadle"]:
            persons = persons.filter(role=role_filter)
        sessions = AttendanceSession.objects.filter(course=course).order_by("date")

        matrix = []

        # per person in the course, create a row with their name, ID number, and attendance
        for person in persons:
            row = {
                "person": person.user.fullname,
                "course_user_id": person.id,
                "attendance": []
            }

            # per class, add a new column to mark attendance
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

            matrix.append(row)

        return render(request, "course_attendance.html", {
            "course": course,
            "sessions": sessions,
            "attendance_matrix": matrix
        })

    def student_view(self, request, course, membership):
        sessions = AttendanceSession.objects.filter(
            course=course
        ).order_by("date")

        records = Attendance.objects.filter(course_user=membership)
        record_map = {r.session_id: r for r in records}

        rows = []
        cuts = 0

        for session in sessions:
            record = record_map.get(session.id)
            status = record.status if record else "absent"

            if status == "absent":
                cuts += 1
            elif status == "late":
                cuts += 0.5

            rows.append({
                "date": session.date,
                "status": status
            })

        total = len(sessions)
        percent = ((total - cuts) / total * 100) if total > 0 else 0

        return render(request, "course_attendance_student.html", {
            "course": course,
            "sessions": rows,
            "cuts": cuts,
            "total_sessions": total,
            "attendance_percentage": round(percent, 2)
        })

class UpdateAttendanceView(LoginRequiredMixin, View):
    def post(self, request):
        course_user_id = request.POST.get("course_user_id")
        session_id = request.POST.get("session_id")
        status = request.POST.get("status")

        if not course_user_id or not session_id:
            return redirect(request.META.get("HTTP_REFERER"))

        course_user = CourseUser.objects.get(id=course_user_id)
        session = AttendanceSession.objects.get(id=session_id)

        record, _ = Attendance.objects.get_or_create(
            course_user=course_user,
            session=session
        )

        record.status = status
        record.save()

        return redirect(request.META.get("HTTP_REFERER"))

class AddSessionView(LoginRequiredMixin, View):
    def post(self, request, course_id):
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

class DeleteSessionView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = AttendanceSession.objects.get(id=session_id)
        course = session.course

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role not in ["professor", "beadle"]:
            raise PermissionDenied

        session.delete()

        return redirect("courses:course_attendance", course.id)