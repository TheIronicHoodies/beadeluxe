from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Course, CourseUser

User = get_user_model()


class TestModels(TestCase):
    def setUp(self):
        username = "Wilson Depot"
        code = "WilDe 11"

        User.objects.create_user(
            username=username,
            password="password"
        )
        user = User.objects.get(username=username)
        user.fullname = username
        user.save()

        course = Course()
        course.code = code
        course.name = "Introduction to Wilson Depot"
        course.save()

        course_user = CourseUser()
        course_user.course = Course.objects.get(code=code)
        course_user.user = User.objects.get(username=username)
        course_user.role = "student"
        course_user.save()

        self.test_course = Course.objects.get(pk=1)
        self.test_course_user = CourseUser.objects.get(pk=1)
        return super().setUp()
    
    def test_string_display(self):
        self.assertEqual(self.test_course.__str__(), "WilDe 11: Introduction to Wilson Depot")
        self.assertEqual(self.test_course_user.__str__(), "Wilson Depot")
    
    def test_absolute_url(self):
        self.assertEqual(self.test_course.get_absolute_url(), "/courses/1/")


class TestViews(TestCase):
    def test(self):
        self.assertHTMLEqual()
    pass



class TestForm(TestCase):
    pass
