from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Attendance, AttendanceSession
from courses.models import Course, CourseUser
import datetime

User = get_user_model()

class TestModels(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username = "Wilson Depot",
            password = "password",
            fullname = "Wilson Depot"
        )

        course = Course()
        course.code = "WilDe 11"
        course.name = "Introduction to Wilson Depot"
        course.save()

        date = datetime.date(2026, 3, 13)

        session = AttendanceSession()
        session.course = course
        session.date = date
        session.save()

        course_user = CourseUser()
        course_user.course = course
        course_user.user = user
        course_user.role = "student"
        course_user.save()

        attendance = Attendance()
        attendance.session = session
        attendance.course_user = course_user
        attendance.status = "absent"
        attendance.save()

        self.test_attendance_session = AttendanceSession.objects.get(pk=1)
        self.test_attendance = Attendance.objects.get(pk=1)
        return super().setUp()
    
    def test_attendance_session_string_display(self):
        self.assertEqual(self.test_attendance_session.__str__(), "WilDe 11 - 2026-03-13")
        pass

    def test_attendance_string_display(self):
        self.assertEqual(self.test_attendance.__str__(), "Wilson Depot - 2026-03-13 - absent")
        pass


class TestAttendancePage(TestCase):
    pass


class TestCourseAttendancePage(TestCase):
    pass


class TestCourseAttendanceStudentPage(TestCase):
    pass
