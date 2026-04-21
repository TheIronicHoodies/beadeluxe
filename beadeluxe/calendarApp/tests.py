from datetime import date, datetime

from .models import Event
from django.test import TestCase
from user_management.forms import User
from courses.models import Course, CourseUser

class AnnouncementTest(TestCase):
    def setUp(self):
        self.professor_user = User.objects.create_user(username="professor", password="pass")
        self.student_user = User.objects.create_user(username="student", password="pass")
        self.beadle_user = User.objects.create_user(username="beadle", password="pass")
        
        self.course = Course.objects.create(name="Test Course", code = "CSCI42")
        
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
        
        self.event = Event.objects.create(
            course=self.course,
            creator=self.beadle_user,
            title="Test Event",
            description="This is a test event.",
            date=date(2024, 12, 31),
            category="assessment",
        )
        
    def test_event_initialization(self):
        self.assertEqual(self.event.title, "Test Event")
        self.assertEqual(self.event.description, "This is a test event.")
        self.assertEqual(self.event.creator, self.beadle_user)
        self.assertEqual(self.event.course, self.course)
        self.assertEqual(self.event.category, "assessment")
        self.assertEqual(str(self.event), "CSCI42 - Test Event (2024-12-31)")
    
    def test_student_can_view_calendar(self):
        self.client.login(username="student", password="pass")
        response = self.client.get(f"/courses/{self.course.id}/calendar/")
        self.assertEqual(response.status_code, 200)
    
    def test_beadle_can_view_calendar(self):
        self.client.login(username="beadle", password="pass")
        response = self.client.get(f"/courses/{self.course.id}/calendar/")
        self.assertEqual(response.status_code, 200)
    
    def test_formatted_date(self):
        self.assertEqual(self.event.formatted_date(), "December 31, 2024")
    
    def test_valid_view_access(self):
        # Beadle can access
        self.client.login(username="beadle", password="pass")
        response = self.client.get(f"/courses/{self.course.id}/calendar/")
        self.assertEqual(response.status_code, 200)

        # Student can access
        self.client.login(username="student", password="pass")
        response = self.client.get(f"/courses/{self.course.id}/calendar/")
        self.assertEqual(response.status_code, 200)

        # Professor can access
        self.client.login(username="professor", password="pass")
        response = self.client.get(f"/courses/{self.course.id}/calendar/")
        self.assertEqual(response.status_code, 200)
        
    def test_add_event_by_beadle(self):
        self.client.login(username="beadle", password="pass")
        response = self.client.post(f"/courses/{self.course.id}/calendar/create/", {
            "title": "New Event",
            "description": "This is a new event.",
            "date": "2024-11-30",
            "category": "deliverable"
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Event.objects.filter(title="New Event").exists())
    
    def test_invalid_add_event(self):
        self.client.login(username="student", password="pass")
        response = self.client.post(f"/courses/{self.course.id}/calendar/create/", {
            "title": "Invalid Event",
            "description": "This event should not be created.",
            "date": "2024-10-31",
            "category": "assessment"
        })
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertFalse(Event.objects.filter(title="Invalid Event").exists())
        
    def test_delete_event_by_beadle(self):
        self.client.login(username="beadle", password="pass")
        response = self.client.post(f"/courses/{self.course.id}/calendar/delete/{self.event.id}/")
        self.assertEqual(response.status_code, 302)  # Redirect after deletion
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
        
    def test_invalid_delete_event(self):
        self.client.login(username="student", password="pass")
        response = self.client.post(f"/courses/{self.course.id}/calendar/delete/{self.event.id}/")
        self.assertEqual(response.status_code, 403)  # Forbidden
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())
        
    def test_edit_event_by_beadle(self):
        self.client.login(username="beadle", password="pass")
        response = self.client.post(f"/courses/{self.course.id}/calendar/edit/{self.event.id}/", {
            "title": "Updated Event",
            "description": "This event has been updated.",
            "date": "2024-09-30",
            "category": "assessment"
        })
        self.assertEqual(response.status_code, 302)  # Redirect after editing
        updated_event = Event.objects.get(id=self.event.id)
        self.assertEqual(updated_event.title, "Updated Event")
        self.assertEqual(updated_event.description, "This event has been updated.")
        self.assertEqual(str(updated_event.date), "2024-09-30")
        self.assertEqual(updated_event.category, "assessment")

