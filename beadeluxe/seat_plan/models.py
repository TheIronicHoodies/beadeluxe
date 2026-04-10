from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from courses.models import Course, CourseUser

# Create your models here.

# represents one seating plan
class SeatPlan(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="seat_plan",
        null=True,
        blank=True
    )

    seat_plan = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through = 
    )

    def __str__(self):
        return '{}_seat_plan'.format(course.name)

    def get_absolute_url(self):
        return reverse('seat_plan', args=[str(course.id)])
    
    class Meta:
        ordering = ['course']
        verbose_name = 'seat_plan'
        verbose_name_plural = 'seat_plans'