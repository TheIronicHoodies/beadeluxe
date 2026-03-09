from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    #basically, there can be more than 1 beadle and 1 professor for each course.
    courseUsers = models.ManyToManyField(User, through="CourseUser") 

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

    user = models.ForeignKey(User, on_delete=models.CASCADE) #not sure if we should use profile or user.
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)

    class Meta:
            constraints = [
        models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course')
    ] #A user can't have 2 roles
