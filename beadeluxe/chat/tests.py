from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Message
from courses.models import Course, CourseUser
from django.urls import reverse
import datetime

User = get_user_model()

# Create your tests here.
class TestModels(TestCase):
    def setUp(self):
        self.professor_user = User.objects.create_user(username="professor", password="pass")
        self.student_user = User.objects.create_user(username="student", password="pass")
        self.beadle_user = User.objects.create_user(username="beadle", password="pass")
        
        self.professor = CourseUser.objects.create(
            user=self.professor_user,
            course=self.course,
            role="professor"
        )

        self.student = CourseUser.objects.create(
            user=self.student_user,
            course=self.course,
            role="student"
        )
        
        self.beadle = CourseUser.objects.create(
            user=self.beadle_user,  
            course=self.course,
            role="beadle"
        )

        course = Course()
        course.code = "WilDe 11"
        course.name = "Introduction to Wilson Depot"
        course.save()

        message = Message()
        message.user = self.student_user
        message.course = course
        message.timestamp = datetime.datetime(2026, 3, 13, 12, 0)
        message.content = "This is a test message."
        message.save()

        self.test_message = Message.objects.get(pk=1)
        return super().setUp()

    def test_message_session_string_display(self):
        self.assertEqual(self.test_message.__str__(), "WilDe 11 - Wilson Depot - 2026-03-13 12:00:00")

    def student_can_view_messages(self):
        url = reverse("chat:messages", args=[self.course.id])
        self.client.login(username="student", password="pass")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that message content is in response
        self.assertContains(response, "This is a test message.")
    
    def student_can_post_messages(self):
        url = reverse("chat:messages", args=[self.course.id])
        self.client.login(username="student", password="pass")

        response = self.client.post(url, {
            "content": "This is another test message.",
            "timestamp": datetime.datetime(2026, 3, 13, 12, 5)
        })

        self.assertEqual(response.status_code, 200)

        # Check that new message content is in response
        self.assertContains(response, "This is another test message.")
    
    def beadle_can_view_messages(self):
        url = reverse("chat:messages", args=[self.course.id])
        self.client.login(username="beadle", password="pass")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that message content is in response
        self.assertContains(response, "This is a test message.")

    def beadle_can_post_messages(self):
        url = reverse("chat:messages", args=[self.course.id])
        self.client.login(username="beadle", password="pass")

        response = self.client.post(url, {
            "content": "This is another test message.",
            "timestamp": datetime.datetime(2026, 3, 13, 12, 5)
        })

        self.assertEqual(response.status_code, 200)

        # Check that new message content is in response
        self.assertContains(response, "This is another test message.")
    
    def professor_cannot_view_messages(self):
        url = reverse("chat:messages", args=[self.course.id])
        self.client.login(username="professor", password="pass")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
    
    
