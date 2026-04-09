from django.db import models
from django.conf import settings
from courses.models import Course
from django.utils.timezone import localtime

class Announcement(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="announcements"
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def formatted_created(self):
        return localtime(self.created_at).strftime("%B %d, %Y %I:%M %p")

    def formatted_updated(self):
        return localtime(self.updated_at).strftime("%B %d, %Y %I:%M %p")

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    class Meta:
        ordering = ["-created_at"]