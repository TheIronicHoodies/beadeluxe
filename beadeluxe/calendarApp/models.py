from django.db import models
from django.conf import settings
from courses.models import Course
from django.utils.timezone import localtime


class Event(models.Model):
    CATEGORY_CHOICES = [
        ("assessment", "Assessment"),
        ("deliverable", "Deliverable"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="events"
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    date = models.DateField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def formatted_date(self):
        return self.date.strftime("%B %d, %Y")

    def formatted_created(self):
        return localtime(self.created_at).strftime("%B %d, %Y %I:%M %p")

    def formatted_updated(self):
        return localtime(self.updated_at).strftime("%B %d, %Y %I:%M %p")

    def __str__(self):
        return f"{self.course.code} - {self.title} ({self.date})"

    class Meta:
        ordering = ["date"]