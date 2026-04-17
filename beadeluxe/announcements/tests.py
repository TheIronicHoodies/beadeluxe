from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from courses.models import CourseUser
from user_management.forms import User
from .models import Announcement, Course
import time

class AnnouncementTest(TestCase):
    # Initialize necessary test data for announcements
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
        
        self.announcement = Announcement.objects.create(
            course=self.course,
            title="Test Announcement",
            content="This is a test announcement.",
            author=self.student_user,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
    
    # Check if announcement details are initialized correctly.
    def test_announcement_initialization(self):
        self.assertEqual(self.announcement.title, "Test Announcement")
        self.assertEqual(self.announcement.content, "This is a test announcement.")
        self.assertEqual(self.announcement.author, self.student_user)
        self.assertEqual(self.announcement.course, self.course)
        self.assertEqual(str(self.announcement), "CSCI42 - Test Announcement")

    # Check if students can view announcements.
    def test_student_can_view_announcements(self):
        url = reverse("announcements:announcement_list", args=[self.course.id])
        self.client.login(username="student", password="pass")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that announcement content is in response
        self.assertContains(response, "Test Announcement")
        self.assertContains(response, "This is a test announcement.")
    
    # Check if beadles can view announcements.
    def test_beadle_can_view_announcements(self):
        url = reverse("announcements:announcement_list", args=[self.course.id])
        self.client.login(username="beadle", password="pass")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that announcement content is in response
        self.assertContains(response, "Test Announcement")
        self.assertContains(response, "This is a test announcement.")

    # Check if professors are forbidden from viewing announcements.
    def test_professor_cant_view_announcements(self):
        url = reverse("announcements:announcement_list", args=[self.course.id])
        self.client.login(username="professor", password="pass")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        # Ensure announcement still exists
        self.assertTrue(Announcement.objects.filter(id=self.announcement.id).exists())

    # Check if beadles can create announcements.
    def test_beadle_can_create_announcement(self):
        url = reverse("announcements:announcement_create", args=[self.course.id])
        self.client.login(username="beadle", password="pass")
        response = self.client.post(url, {
            "title": "Beadle Announcement",
            "content": "This is a beadle announcement."
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Announcement.objects.filter(title="Beadle Announcement").exists())
    
    # Check if students and professors cannot create announcements.
    def test_invalid_create_announcement(self):
        url = reverse("announcements:announcement_create", args=[self.course.id])
        self.client.login(username="student", password="pass")
        response = self.client.post(url, {
            "title": "Student Announcement",
            "content": "This is a student announcement."
        })
        self.assertEqual(response.status_code, 403)

        self.client.login(username="professor", password="pass")
        response = self.client.post(url, {
            "title": "Professor Announcement",
            "content": "This is a professor announcement."
        })
        self.assertEqual(response.status_code, 403)

    # Check if beadles can delete announcements.     
    def test_beadle_can_delete_announcement(self):
        url = reverse("announcements:announcement_delete", args=[self.course.id, self.announcement.id])
        self.client.login(username="beadle", password="pass")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Announcement.objects.filter(id=self.announcement.id).exists())

    # Check if students and professors are forbidden from deleting announcements.
    def test_invalid_delete_announcement(self):
        url = reverse("announcements:announcement_delete", args=[self.course.id, self.announcement.id])
        self.client.login(username="student", password="pass")
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Announcement.objects.filter(id=self.announcement.id).exists())
        
        url = reverse("announcements:announcement_delete", args=[self.course.id, self.announcement.id])
        self.client.login(username="professor", password="pass")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Announcement.objects.filter(id=self.announcement.id).exists())
        
    # Check if editing announcements works correctly.
    def test_announcement_update(self):
        old_updated_at = self.announcement.updated_at

        self.announcement.title = "Updated Announcement"
        self.announcement.content = "This announcement has been updated."
        
        time.sleep(1) # Make sure time moves 1 second to ensure updated_at changes
        
        self.announcement.save()
        self.announcement.refresh_from_db()

        self.assertEqual(self.announcement.title, "Updated Announcement")
        self.assertEqual(self.announcement.content, "This announcement has been updated.")
        
        # Checking if updated_at changes
        self.assertNotEqual(self.announcement.updated_at, old_updated_at) 
        self.assertTrue(self.announcement.updated_at >= old_updated_at)
        
        # Checking if created_at and updated_at are different after updating
        self.assertNotEqual(self.announcement.created_at, self.announcement.updated_at) 
        
    
