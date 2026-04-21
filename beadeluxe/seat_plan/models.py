from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from courses.models import Course, CourseUser

# Create your models here.

# represents one seating plan
class SeatAssignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    course_user = models.ForeignKey(CourseUser, on_delete=models.CASCADE)

    row = models.PositiveIntegerField()
    col = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course_user.user.fullname} - {self.course.name} ({self.row}, {self.col})"

    class Meta:
        unique_together = [
            ("course", "row", "col"), # Only one user per seat
            ("course_user",) # Only have one seat per course
        ]