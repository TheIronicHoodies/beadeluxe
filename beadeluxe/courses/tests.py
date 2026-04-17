from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Course, CourseUser, LAYOUT_TEMPLATES
from django.urls import reverse

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
    
    def test_course_string_display(self):
        self.assertEqual(self.test_course.__str__(), "WilDe 11: Introduction to Wilson Depot")

    def test_course_user_string_display(self):
        self.assertEqual(self.test_course_user.__str__(), "Wilson Depot")
    
    def test_absolute_url(self):
        self.assertEqual(self.test_course.get_absolute_url(), "/courses/1/")

    def test_layout_auto_generated_on_save(self):
        course = Course(code="LH 23", name="Lecture Hall", layout_type="lecture")
        course.save()

        self.assertEqual(course.layout, LAYOUT_TEMPLATES["lecture"])

    def test_layout_matches_selected_type(self):
        course = Course(code="DIL 12.1", name="Donuts in Life", layout_type="donut")
        course.save()

        self.assertEqual(course.layout, LAYOUT_TEMPLATES["donut"])

    def test_layout_updates_when_type_changes(self):
        course = Course(code="CET 67", name="Compact Engineering Tests", layout_type="lecture")
        course.save()

        course.layout_type = "compact"
        course.save()

        self.assertEqual(course.layout, LAYOUT_TEMPLATES["compact"])

    def test_generate_layout_returns_correct_template(self):
        course = Course(code="EE 32", name="Extra-difficult Examinations", layout_type="exam")

        layout = course.generate_layout()

        self.assertEqual(layout, LAYOUT_TEMPLATES["exam"])


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        
        User.objects.create_user(
            username="Wilson Depot",
            password="password"
        )

        User.objects.create_user(
            username="Wilson's Son",
            email="a@test.com",
            password="password",
            fullname="Wilson's Son",
        )

        course_Two = Course()
        course_Two.code = "WilDe 12"
        course_Two.name = "Introduction to Wilson Depot 2"
        course_Two.save()

        course_user_Two = CourseUser()
        course_user_Two.course = Course.objects.get(code="WilDe 12")
        course_user_Two.user = User.objects.get(username="Wilson Depot")
        course_user_Two.role = "beadle"
        course_user_Two.save()

        return super().setUp()
    
    def test_add_course(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:list')
        data = {
            'course_name': "Introduction to Wilson Depot",
            'course_code': "WilDe 11",
        }

        response = self.client.post(path=url, data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Course.objects.filter(code="WilDe 11").exists())
        course = Course.objects.get(code="WilDe 11")
        user = User.objects.get(username="Wilson Depot")
        course_user = CourseUser.objects.get(user=user, course=course)
        self.assertTrue(course_user.role=="beadle")
    
    def test_add_member(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:detail', args=[1])
        data = {
            'form_type': "addMember",
            'email': "a@test.com",
            'role': "student",
        }

        response = self.client.post(path=url, data=data)

        self.assertEqual(response.status_code, 200)
        course = Course.objects.get(code="WilDe 12")
        user = User.objects.get(username="Wilson's Son")
        self.assertTrue(CourseUser.objects.filter(course=course, user=user).exists())
        course_user = CourseUser.objects.get(user=user, course=course)
        self.assertTrue(course_user.role=="student")
    
    def test_assign_beadle(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )

        course_user_Two = CourseUser()
        course_user_Two.course = Course.objects.get(code="WilDe 12")
        course_user_Two.user = User.objects.get(username="Wilson's Son")
        course_user_Two.role = "student"
        course_user_Two.save()
        
        url = reverse('courses:detail', args=[1])
        data = {
            'form_type': "assignBeadle",
            'fullname': "Wilson's Son",
        }

        response = self.client.post(path=url, data=data)

        self.assertEqual(response.status_code, 200)
        course = Course.objects.get(code="WilDe 12")
        user = User.objects.get(username="Wilson's Son")
        course_user = CourseUser.objects.get(user=user, course=course)
        self.assertTrue(course_user.role=="beadle")
    
    def test_resign(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )

        course_user_Two = CourseUser()
        course_user_Two.course = Course.objects.get(code="WilDe 12")
        course_user_Two.user = User.objects.get(username="Wilson's Son")
        course_user_Two.role = "beadle"
        course_user_Two.save()
        
        url = reverse('courses:detail', args=[1])
        data = {
            'form_type': "resign",
        }

        response = self.client.post(path=url, data=data)

        self.assertEqual(response.status_code, 200)
        course = Course.objects.get(code="WilDe 12")
        user = User.objects.get(username="Wilson Depot")
        course_user = CourseUser.objects.get(user=user, course=course)
        self.assertTrue(course_user.role=="student")



class TestCoursesListPage(TestCase):
    def setUp(self):
        self.client = Client()
        
        User.objects.create_user(
            username="Wilson Depot",
            password="password"
        )

        course_One = Course()
        course_One.code = "WilDe 11"
        course_One.name = "Introduction to Wilson Depot"
        course_One.save()

        course_user_One = CourseUser()
        course_user_One.course = Course.objects.get(code="WilDe 11")
        course_user_One.user = User.objects.get(username="Wilson Depot")
        course_user_One.role = "student"
        course_user_One.save()

        course_Two = Course()
        course_Two.code = "WilDe 12"
        course_Two.name = "Introduction to Wilson Depot 2"
        course_Two.save()

        course_user_Two = CourseUser()
        course_user_Two.course = Course.objects.get(code="WilDe 12")
        course_user_Two.user = User.objects.get(username="Wilson Depot")
        course_user_Two.role = "student"
        course_user_Two.save()
        
        User.objects.create_user(
            username="Wilson's Son",
            password="password"
        )

        return super().setUp()
    
    def test_page_response_if_not_logged_in(self):
        url = reverse('courses:list')
        response = self.client.get(url)
        self.assertRedirects(response, '/accounts/login/?next=/courses/', status_code=302, target_status_code=200)

    def test_page_response_if_logged_in(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:list')
        response = self.client.get(url)
        self.assertEqual(response.request['PATH_INFO'], '/courses/')

    def test_if_course_is_displayed(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:list')
        response = self.client.get(url)
        self.assertInHTML('<a href="/courses/1/">WilDe 11: Introduction to Wilson Depot</a>', response.text)
    
    def test_if_multiple_courses_displayed(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:list')
        response = self.client.get(url)
        self.assertInHTML('<a href="/courses/2/">WilDe 12: Introduction to Wilson Depot 2</a>', response.text)
    
    def test_if_courses_not_member_of_displayed(self):
        self.client.login(
            username="Wilson's Son",
            password="password"
        )
        url = reverse('courses:list')
        response = self.client.get(url)

        self.assertNotInHTML('<a href="/courses/1/">WilDe 11: Introduction to Wilson Depot</a>', response.text)


class TestCoursesDetailPage(TestCase):
    def setUp(self):
        self.client = Client()
        
        User.objects.create_user(
            username="Wilson Depot",
            password="password"
        )
        
        User.objects.create_user(
            username="Wilson's Son",
            password="password"
        )

        course_One = Course()
        course_One.code = "WilDe 11"
        course_One.name = "Introduction to Wilson Depot"
        course_One.save()

        course_user_One = CourseUser()
        course_user_One.course = Course.objects.get(code="WilDe 11")
        course_user_One.user = User.objects.get(username="Wilson Depot")
        course_user_One.role = "beadle"
        course_user_One.save()

        course_user_Two = CourseUser()
        course_user_Two.course = Course.objects.get(code="WilDe 11")
        course_user_Two.user = User.objects.get(username="Wilson's Son")
        course_user_Two.role = "student"
        course_user_Two.save()

        return super().setUp()
    
    def test_page_response_if_not_logged_in(self):
        url = reverse('courses:detail', args=[1])
        response = self.client.get(url)

        # Deliberating whether to change this functionality
        self.assertRedirects(response, '/accounts/login/?next=/courses/1/', status_code=302, target_status_code=200)

    def test_page_response_if_logged_in(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:detail', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.request['PATH_INFO'], '/courses/1/')
    
    def test_display_if_not_beadle(self):
        self.client.login(
            username="Wilson's Son",
            password="password"
        )
        url = reverse('courses:detail', args=[1])
        response = self.client.get(url)
        self.assertNotInHTML('<p>Add a Member</p>', response.text)

    def test_display_if_one_beadle(self):
        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:detail', args=[1])
        response = self.client.get(url)
        self.assertInHTML('<p>Add a Member</p>', response.text)
        self.assertNotInHTML('<input type="submit" value="Resign">', response.text)
    
    def test_display_if_two_beadles(self):
        User.objects.create_user(
            username="Wilson's Colleague",
            password="password"
        )

        course_user_One = CourseUser()
        course_user_One.course = Course.objects.get(code="WilDe 11")
        course_user_One.user = User.objects.get(username="Wilson's Colleague")
        course_user_One.role = "beadle"
        course_user_One.save()

        self.client.login(
            username="Wilson Depot",
            password="password"
        )
        url = reverse('courses:detail', args=[1])
        response = self.client.get(url)

        self.assertInHTML('<input type="submit" value="Resign">', response.text)

    