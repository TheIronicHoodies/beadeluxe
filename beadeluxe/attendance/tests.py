from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Attendance, AttendanceSession
from courses.models import Course, CourseUser
from django.urls import reverse
import datetime

User = get_user_model()

class TestModels(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="Wilson Depot",
            password="password",
            fullname="Wilson Depot",
            nickname="WD",
            pronouns="he/him",
            mobile_number="+1234567890"
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

    def test_attendance_string_display(self):
        self.assertEqual(self.test_attendance.__str__(), "Wilson Depot - 2026-03-13 - absent")

    def test_attendance_session_unique_constraint(self):
        # Test that AttendanceSession forces unique course-date
        course = Course.objects.get(code="WilDe 11")
        with self.assertRaises(Exception):  # Should raise IntegrityError
            AttendanceSession.objects.create(course=course, date=datetime.date(2026, 3, 13))

    def test_attendance_unique_constraint(self):
        # Test that Attendance forces session-course_user
        session = AttendanceSession.objects.get(pk=1)
        course_user = CourseUser.objects.get(pk=1)
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Attendance.objects.create(session=session, course_user=course_user, status="present")

class TestCourseAttendanceStudentPage(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.student_user = User.objects.create_user(
            username="Wilson Student",
            password="password",
            fullname="Test Student",
            nickname="TS",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.course = Course.objects.create(
            code="TEST101",
            name="Test Course"
        )

        CourseUser.objects.create(
            user=self.student_user,
            course=self.course,
            role="student"
        )

        # Create sessions with attendance
        session1 = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 12)
        )

        session2 = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 13)
        )

        course_user = CourseUser.objects.get(user=self.student_user, course=self.course)
        
        Attendance.objects.create(
            session=session1,
            course_user=course_user,
            status="present"
        )

        Attendance.objects.create(
            session=session2,
            course_user=course_user,
            status="late"
        )

        return super().setUp()
    
    def test_student_attendance_display(self):
        # Test that student attendance page shows correct cuts and percentage
        self.client.login(username="Wilson Student", password="password")
        url = reverse('courses:course_attendance', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 1 present, 1 late = 0.5 cuts, attendance = 75%
        self.assertContains(response, "Cuts (Absences): <strong>0.5</strong>")
        self.assertContains(response, "Attendance: 75.0%")

class TestCourseAttendancePage(TestCase):
    pass

class TestViews(TestCase):
    pass