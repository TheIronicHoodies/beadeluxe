from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Attendance, AttendanceSession
from courses.models import Course, CourseUser
import datetime

User = get_user_model()

class TestModels(TestCase):
    # Verify attendance model, string formatting, and uniqueness
    def setUp(self):
        self.user = User.objects.create_user(
            username="Wilson Depot",
            password="password",
            fullname="Wilson Depot",
            nickname="WD",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.course = Course.objects.create(code="WilDe 11", name="Introduction to Wilson Depot")

        self.course_user = CourseUser.objects.create(
            user=self.user,
            course=self.course,
            role="student"
        )

        self.session = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 13)
        )

        Attendance.objects.create(
            session=self.session,
            course_user=self.course_user,
            status="absent"
        )

    def test_session_unique_course_date(self):
        # Test that AttendanceSession forces unique course-date
        course = Course.objects.get(code="WilDe 11")
        with self.assertRaises(Exception):  # Should raise IntegrityError
            AttendanceSession.objects.create(course=course, date=datetime.date(2026, 3, 13))

    def test_session_unique_course_user(self):
        # Test that Attendance forces unique session-course_user combo
        session = AttendanceSession.objects.get(pk=1)
        course_user = CourseUser.objects.get(pk=1)
        with self.assertRaises(Exception):  # Should raise IntegrityError
            Attendance.objects.create(session=session, course_user=course_user, status="present")

class TestAttendanceSummaryView(TestCase):
    # Verify attendance summary page for enrolled users and cut/attendance calculation
    def setUp(self):
        self.client = Client()
        
        self.student_user = User.objects.create_user(
            username="Wilson Student",
            password="password",
            fullname="Wilson Loverboy",
            nickname="WL",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.professor_user = User.objects.create_user(
            username="Wilson Professor",
            password="password",
            fullname="Jonathan Professor",
            nickname="JP",
            pronouns="he/him",
            mobile_number="+1234567891"
        )

        self.course = Course.objects.create(code="AttSP 5", name="Attending Summary Pages")

        self.student_course_user = CourseUser.objects.create(
            user=self.student_user,
            course=self.course,
            role="student"
        )

        self.professor_course_user = CourseUser.objects.create(
            user=self.professor_user,
            course=self.course,
            role="professor"
        )

        self.session1 = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 12)
        )

        self.session2 = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 13)
        )

        Attendance.objects.create(
            session=self.session1,
            course_user=self.student_course_user,
            status="present"
        )

    def test_attendance_view_redirects_when_anonymous(self):
        # Anonymous users should be sent to login when opening attendance summary
        url = reverse('attendance:attendance')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_student_attendance_summary_shows_cuts_and_percentage(self):
        # The student attendance summary should count absences as cuts and calculate percentaage
        self.client.login(username="Wilson Student", password="password")
        url = reverse('attendance:attendance')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AttSP 5")
        self.assertContains(response, "Total Sessions: 2")
        self.assertContains(response, "Cuts (Absences): <strong>1</strong>")
        self.assertContains(response, "🟢")
        self.assertContains(response, "🔴")

    def test_professor_attendance_summary_access(self):
        # Professors should be able to view their own attendance summary page
        self.client.login(username="Wilson Professor", password="password")
        url = reverse('attendance:attendance')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AttSP 5")

    def test_attendance_summary_with_present_and_absent(self):
        # Mixed attendance records should minus cut total when records exist
        Attendance.objects.create(
            session=self.session2,
            course_user=self.student_course_user,
            status="present"
        )
        self.client.login(username="Wilson Student", password="password")
        url = reverse('attendance:attendance')
        response = self.client.get(url)
        self.assertContains(response, "Cuts (Absences): <strong>0</strong>")


class TestCourseAttendanceView(TestCase):
    # Verify course attendance detail views for professors/beadles and students
    def setUp(self):
        self.client = Client()

        self.student_user = User.objects.create_user(
            username="Wilson Student",
            password="password",
            fullname="Wilson Loverboy",
            nickname="WL",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.professor_user = User.objects.create_user(
            username="Wilson Professor",
            password="password",
            fullname="Jonathan Professor",
            nickname="JP",
            pronouns="he/him",
            mobile_number="+1234567891"
        )

        self.beadle_user = User.objects.create_user(
            username="Wilson Beadle",
            password="password",
            fullname="Wilson Beetle",
            nickname="WB",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.course = Course.objects.create(code="CAD 311", name="Computer Attendance Detail")

        self.student_course_user = CourseUser.objects.create(
            user=self.student_user,
            course=self.course,
            role="student"
        )

        self.professor_course_user = CourseUser.objects.create(
            user=self.professor_user,
            course=self.course,
            role="professor"
        )

        self.beadle_course_user = CourseUser.objects.create(
            user=self.beadle_user,
            course=self.course,
            role="beadle"
        )

        self.session1 = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 12)
        )

        self.session2 = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 13)
        )

    def test_professor_course_attendance_page(self):
        # Professors should see the attendance matrix for all enrolled course users
        self.client.login(username="Wilson Professor", password="password")
        url = reverse('courses:course_attendance', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wilson Loverboy")
        self.assertContains(response, "Jonathan Professor")

    def test_beadle_course_attendance_page(self):
        # Beadles should be able to view the same attendance matrix as professors
        self.client.login(username="Wilson Beadle", password="password")
        url = reverse('courses:course_attendance', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_student_course_attendance_page(self):
        # Students should see their own course atendance details and cut count
        self.client.login(username="Wilson Student", password="password")
        url = reverse('courses:course_attendance', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Sessions: 2")
        self.assertContains(response, "Cuts (Absences): <strong>2</strong>")

    def test_student_course_attendance_late_calculation(self):
        # Late attendance should count as half a cut for students.
        Attendance.objects.create(
            session=self.session1,
            course_user=self.student_course_user,
            status="late"
        )
        self.client.login(username="Wilson Student", password="password")
        url = reverse('courses:course_attendance', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertIn("1.5", response.content.decode())

    def test_nonmember_cannot_view_course_attendance(self):
        # Users not enrolled in the course should receive a permission denied response when opening the page
        self.outsider_user = User.objects.create_user(
            username="Wilson Outsider",
            password="password",
            fullname="Wilson Neverland",
            nickname="WN",
            pronouns="he/him",
            mobile_number="+1234567893"
        )
        self.client.login(username="Wilson Outsider", password="password")
        url = reverse('courses:course_attendance', kwargs={'pk': self.course.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TestAttendanceActionsView(TestCase):
    # Verify create/update/delete attendance actions and permission enforcement
    def setUp(self):
        self.client = Client()

        self.professor_user = User.objects.create_user(
            username="Wilson Professor",
            password="password",
            fullname="Jonathan Professor",
            nickname="JP",
            pronouns="he/him",
            mobile_number="+1234567891"
        )

        self.beadle_user = User.objects.create_user(
            username="Wilson Beadle",
            password="password",
            fullname="Wilson Beetle",
            nickname="WB",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.student_user = User.objects.create_user(
            username="Wilson Student",
            password="password",
            fullname="Wilson Loverboy",
            nickname="WL",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.course = Course.objects.create(code="CUD 41", name="Creation Updation Deletion")

        self.professor_course_user = CourseUser.objects.create(
            user=self.professor_user,
            course=self.course,
            role="professor"
        )

        self.beadle_course_user = CourseUser.objects.create(
            user=self.beadle_user,
            course=self.course,
            role="beadle"
        )

        self.student_course_user = CourseUser.objects.create(
            user=self.student_user,
            course=self.course,
            role="student"
        )

        self.session = AttendanceSession.objects.create(
            course=self.course,
            date=datetime.date(2026, 3, 13)
        )

    def test_update_attendance_creates_record(self):
        # Posting a status update should create or update the Attendance record
        self.client.login(username="Wilson Professor", password="password")
        url = reverse('attendance:update_attendance')
        response = self.client.post(
            url,
            {
                'course_user_id': self.student_course_user.id,
                'session_id': self.session.id,
                'status': 'present'
            },
            HTTP_REFERER='/'
        )
        self.assertEqual(response.status_code, 302)
        attendance = Attendance.objects.get(session=self.session, course_user=self.student_course_user)
        self.assertEqual(attendance.status, 'present')

    def test_update_attendance_missing_parameters_redirects(self):
        # Missing required parameters should redirect back without creating attendance
        self.client.login(username="Wilson Professor", password="password")
        url = reverse('attendance:update_attendance')
        response = self.client.post(url, {}, HTTP_REFERER='/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_add_session_as_professor(self):
        # Professors can add new AttendanceSession for their course
        self.client.login(username="Wilson Professor", password="password")
        url = reverse('attendance:add_session', kwargs={'course_id': self.course.id})
        response = self.client.post(url, {'session_date': '2026-03-14'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AttendanceSession.objects.filter(course=self.course, date='2026-03-14').exists())

    def test_delete_session_as_professor(self):
        # Professors can delete existing attendance sessions and cascade attendance records
        self.client.login(username="Wilson Professor", password="password")
        url = reverse('attendance:delete_session', kwargs={'session_id': self.session.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(AttendanceSession.objects.filter(id=self.session.id).exists())

    def test_add_session_as_student_forbidden(self):
        # Students should not be allowed to add attendance sessions
        self.client.login(username="Wilson Student", password="password")
        url = reverse('attendance:add_session', kwargs={'course_id': self.course.id})
        response = self.client.post(url, {'session_date': '2026-03-14'})
        self.assertEqual(response.status_code, 403)

    def test_delete_session_as_student_forbidden(self):
        # Students should not be permitted to delete attendance sessions.
        self.client.login(username="Wilson Student", password="password")
        url = reverse('attendance:delete_session', kwargs={'session_id': self.session.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)


class TestAttendanceCalculationLogic(TestCase):
    # Verify calculation rules for cuts, including late attendance and remaining cuts
    def setUp(self):
        self.user = User.objects.create_user(
            username="Wilson Calculator",
            password="password",
            fullname="Wilson Calculatorix",
            nickname="WCx",
            pronouns="he/him",
            mobile_number="+1234567890"
        )

        self.course = Course.objects.create(code="Calc 21", name="Calculationatorix")
        self.course_user = CourseUser.objects.create(user=self.user, course=self.course, role="student")

        self.session_absent = AttendanceSession.objects.create(course=self.course, date=datetime.date(2026, 3, 12))
        self.session_late = AttendanceSession.objects.create(course=self.course, date=datetime.date(2026, 3, 13))

        Attendance.objects.create(session=self.session_absent, course_user=self.course_user, status="absent")
        Attendance.objects.create(session=self.session_late, course_user=self.course_user, status="late")

    def test_cuts_and_remaining_calculation(self):
        # Calculate total cuts and remaining allowance for a student with absent and late records
        sessions = AttendanceSession.objects.filter(course=self.course)
        records = Attendance.objects.filter(course_user=self.course_user)
        record_map = {record.session_id: record for record in records}

        cuts = 0
        for session in sessions:
            record = record_map.get(session.id)
            status = record.status if record else "absent"
            if status == "absent":
                cuts += 1
            elif status == "late":
                cuts += 0.5

        remaining_allowed = 3 - cuts
        self.assertEqual(cuts, 1.5)
        self.assertEqual(remaining_allowed, 1.5)