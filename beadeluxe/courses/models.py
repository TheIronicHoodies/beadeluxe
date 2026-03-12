from django.db import models
from django.urls import reverse
from django.conf import settings
from django.views.generic import DetailView

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    #basically, there can be more than 1 beadle and 1 professor for each course.
    courseUsers = models.ManyToManyField(settings.AUTH_USER_MODEL, through="CourseUser") 

    def __str__(self):
        return '{}: {}'.format(self.code, self.name)

    def get_absolute_url(self):
        return reverse('course_detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['name']
        verbose_name = 'course'
        verbose_name_plural = 'courses'

class CourseUser(models.Model):
    ROLES = [
        ("student", "Student"),
        ("beadle", "Beadle"),
        ("professor", "Professor"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) #not sure if we should use profile or user.
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)

    class Meta:
            constraints = [
        models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course')
    ] #A user can't have 2 roles

    def __str__(self):
        user = self.user.fullname if self.user else "Unknown User"
        course = self.course.code if self.course else "Unknown Course"
        return f"{user} - {course} - {self.role}"