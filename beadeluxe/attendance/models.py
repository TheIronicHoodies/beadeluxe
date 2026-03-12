from django.db import models
from django.conf import settings
from courses.models import Course, CourseUser


class AttendanceSession(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sessions",
        null=True,
        blank=True
    )

    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "date")

    def __str__(self):
        return f"{self.course.code} - {self.date}"

class Attendance(models.Model):

    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
    ]

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        null=True,
        blank=True
    )

    course_user = models.ForeignKey(
        CourseUser,
        on_delete=models.CASCADE,
        related_name="attendance_records",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="absent"
    )

    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("session", "course_user")

    def __str__(self):
        session_date = self.session.date if self.session else "No session"
        user_name = self.course_user.user.fullname if self.course_user else "Unknown user"
        return f"{user_name} - {session_date} - {self.status}"