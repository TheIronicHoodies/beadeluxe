from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Announcement, Course

class AnnouncementTest(TestCase):
    def setUp(self): 
        self.user = get_user_model().objects.create_user(
            username="collin",
            password="secret123"
        )
        
        self.course = Course.objects.create(
            code="CS101", 
            name="Introduction to Computer Science"
        )
    
        self.announcement = Announcement.objects.create(
            title="Test Announcement",
            content="This is a test announcement.",
            author=self.user,
            course=self.course,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        
    def test_initialization(self):
        self.assertEqual(self.user.username, "collin")
        self.assertEqual(self.user.check_password("secret123"), True)
        
        self.assertEqual(self.course.name, "Introduction to Computer Science") 
        self.assertEqual(self.course.code, "CS101")
        
        self.assertEqual(self.announcement.title, "Test Announcement")
        self.assertEqual(self.announcement.content, "This is a test announcement.")
        self.assertEqual(self.announcement.author, self.user)
        self.assertEqual(self.announcement.course, self.course)
        self.assertEqual(str(self.announcement), "CS101 - Test Announcement")
    
    def test_announcement_create(self):
        announcement = Announcement(
            title="Another Announcement",
            content="This is another test announcement.",
            author=self.user,
            course=self.course,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        self.assertEqual(announcement.title, "Another Announcement")
        self.assertEqual(announcement.content, "This is another test announcement.")
        self.assertEqual(announcement.author, self.user)
        self.assertEqual(announcement.course, self.course)
        self.assertIsNotNone(announcement.created_at)
        self.assertIsNotNone(announcement.updated_at)
        
    def test_announcement_update(self):
        old_updated_at = self.announcement.updated_at

        self.announcement.title = "Updated Announcement"
        self.announcement.content = "This announcement has been updated."
        self.announcement.save()

        self.announcement.refresh_from_db()

        self.assertEqual(self.announcement.title, "Updated Announcement")
        self.assertEqual(self.announcement.content, "This announcement has been updated.")
        
        # Checking if updated_at changes
        self.assertNotEqual(self.announcement.updated_at, old_updated_at) 
        # Checking if updated_at is more recent
        self.assertTrue(self.announcement.updated_at > old_updated_at) 
        # Checking if created_at and updated_at are different after updating
        self.assertNotEqual(self.announcement.created_at, self.announcement.updated_at) 
        
    
