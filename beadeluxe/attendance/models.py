from django.db import models

# Create your models here.
class Attendance(models.Model):
    student_name = models.CharField(max_length=100)
    date = models.DateField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student_name} - {self.date}"