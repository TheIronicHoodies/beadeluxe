import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from courses.models import Course, CourseUser
from .models import SeatAssignment

User = get_user_model()

# just to shorten creating users
def create_user(username, fullname):
    return User.objects.create_user(
        username=username,
        password="pass",
        fullname=fullname,
        nickname=username,
        pronouns="they/them",
        mobile_number="+92081356621",
    )

# Create your tests here.
class TestModels(TestCase):
    def setUp(self):
        self.course = Course.objects.create(code="ISP 101", name="Intro to Seat Plans")
        self.student_user = create_user("student", "Wilson Uno")
        self.student = CourseUser.objects.create(
            user=self.student_user,
            course=self.course,
            role="student",
        )

class TestViews(TestCase):
    def setUp(self):
        self.course = Course.objects.create(code="TBR 20.1", name="Testing Butt Rests")
        self.professor_user = create_user("professor", "Professor X")
        self.student_user = create_user("student", "Wilson One")
        self.other_student_user = create_user("student2", "Wilson Two")
        self.beadle_user = create_user("beadle", "Beadle One")

        self.professor = CourseUser.objects.create(
            user=self.professor_user,
            course=self.course,
            role="professor",
        )
        self.student = CourseUser.objects.create(
            user=self.student_user,
            course=self.course,
            role="student",
        )
        self.other_student = CourseUser.objects.create(
            user=self.other_student_user,
            course=self.course,
            role="student",
        )
        self.beadle = CourseUser.objects.create(
            user=self.beadle_user,
            course=self.course,
            role="beadle",
        )

    # Course students can view the seat plan page
    def test_student_of_course_can_view_seat_plan(self):
        self.client.login(username="student", password="pass")
        response = self.client.get(reverse("seat_plan:seat_plan", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertIn("seat_plan", response.context)

    # Students can only see themselves in the student list, not other students or beadles
    def test_student_can_see_population_list(self):
        self.client.login(username="student", password="pass")
        response = self.client.get(reverse("seat_plan:seat_plan", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["students"]), 1)
        self.assertEqual(response.context["students"][0].user, self.student_user)


    # Students can assign their own seat, but not other students' seats
    def test_student_cannot_assign_another_student(self):
        self.client.login(username="student", password="pass")
        response = self.client.post(
            reverse("seat_plan:update_seat_plan"),
            data=json.dumps({
                "student_id": self.other_student.id,
                "row": 0,
                "col": 0,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            SeatAssignment.objects.filter(course_user=self.other_student).exists()
        )

    # Course students can view the seat plan page
    def test_student_of_course_can_view_seat_plan(self):
        self.client.login(username="student", password="pass")
        response = self.client.get(reverse("seat_plan:seat_plan", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertIn("seat_plan", response.context)

    # Students can only see themselves in the student list, not other students or beadles
    def test_student_can_see_population_list(self):
        self.client.login(username="student", password="pass")
        response = self.client.get(reverse("seat_plan:seat_plan", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["students"]), 1)
        self.assertEqual(response.context["students"][0].user, self.student_user)


    # Students can assign their own seat, but not other students' seats
    def test_student_cannot_assign_another_student(self):
        self.client.login(username="student", password="pass")
        response = self.client.post(
            reverse("seat_plan:update_seat_plan"),
            data=json.dumps({
                "student_id": self.other_student.id,
                "row": 0,
                "col": 0,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            SeatAssignment.objects.filter(course_user=self.other_student).exists()
        )

    # Students can remove only their own seat assignment
    def test_student_can_remove_own_assignment(self):
        self.client.login(username="student", password="pass")
        # First, assign a seat to the student
        SeatAssignment.objects.create(
            course=self.course,
            course_user=self.student,
            row=1,
            col=1,
        )

        response = self.client.post(
            reverse("seat_plan:remove_seat"),
            data=json.dumps({"student_id": self.student.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "removed"})
        self.assertFalse(
            SeatAssignment.objects.filter(course_user=self.student).exists()
        )

    # Beadles can view the course seat plan and sees the full student list, including beadles
    def test_beadle_can_view_student_population_list(self):
        self.client.login(username="beadle", password="pass")
        response = self.client.get(reverse("seat_plan:seat_plan", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["students"]), 3)
        self.assertCountEqual(
            [student.user for student in response.context["students"]],
            [self.student_user, self.other_student_user, self.beadle_user]
        )

    # Only a beadle can assign seats and save changes to the seat plan
    def test_beadle_can_assign_student_to_seat(self):
        self.client.login(username="beadle", password="pass")
        response = self.client.post(
            reverse("seat_plan:update_seat_plan"),
            data=json.dumps({
                "student_id": self.student.id,
                "row": 1,
                "col": 2,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})
        self.assertTrue(
            SeatAssignment.objects.filter(
                course_user=self.student,
                course=self.course,
                row=1,
                col=2,
            ).exists()
        )

    # Beadle can remove an assigned seat
    def test_beadle_can_remove_assigned_seat(self):
        self.client.login(username="beadle", password="pass")
        # Assign a seat first
        SeatAssignment.objects.create(
            course=self.course,
            course_user=self.student,
            row=1,
            col=1,
        )

        response = self.client.post(
            reverse("seat_plan:remove_seat"),
            data=json.dumps({"student_id": self.student.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            SeatAssignment.objects.filter(course_user=self.student).exists()
        )

    # Beadle can automatically assign students and beadles alphabetically
    def test_beadle_can_auto_assign_alphabetical(self):
        self.client.login(username="beadle", password="pass")
        response = self.client.post(
            reverse("seat_plan:auto_assign", kwargs={"pk": self.course.pk}),
            data={"mode": "alphabetical"},
        )

        self.assertEqual(response.status_code, 302)

        assignments = list(SeatAssignment.objects.filter(course=self.course).order_by("row", "col"))
        self.assertEqual([assignment.course_user for assignment in assignments], [self.beadle, self.student, self.other_student])

    # Beadle can automatically assign students and beadles in random order
    def test_beadle_can_auto_assign_random(self):
        self.client.login(username="beadle", password="pass")

        response = self.client.post(
            reverse("seat_plan:auto_assign", kwargs={"pk": self.course.pk}),
            data={"mode": "random"},
        )

        self.assertEqual(response.status_code, 302)

        assignments = list(
            SeatAssignment.objects.filter(course=self.course)
        )
        assigned_users = [a.course_user for a in assignments]

        # correct number of assignments
        self.assertEqual(len(assignments), 3)

        # all expected users are present
        self.assertEqual(
            set(assigned_users),
            {self.beadle, self.student, self.other_student}
        )

        # no duplicates
        self.assertEqual(len(assigned_users), len(set(assigned_users)))

    # Users not enrolled in the course cannot view the seat plan
    def test_non_member_cannot_view_seat_plan(self):
        outsider = create_user("outsider", "Outside User")
        self.client.login(username="outsider", password="pass")

        response = self.client.get(reverse("seat_plan:seat_plan", kwargs={"pk": self.course.pk}))
        self.assertEqual(response.status_code, 403)