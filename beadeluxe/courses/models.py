from django.db import models
from django.urls import reverse

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    # To be implemented
    # beadle = models.CharField()
    # professor = models.CharField()
    # students = models.CharField()

    def __str__(self):
        return '{}: {}'.format(self.code, self.name)

    def get_absolute_url(self):
        return reverse('course_detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['name']
        verbose_name = 'course'
        verbose_name_plural = 'courses'
