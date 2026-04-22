from django.db import models
from django.urls import reverse
from django.conf import settings
from django.views.generic import DetailView

LAYOUT_TEMPLATES = {
    "lecture": [
        [1,1,1,1,0,1,1,1,1],
        [1,1,1,1,0,1,1,1,1],
        [1,1,1,1,0,1,1,1,1],
        [1,1,1,1,0,1,1,1,1],
    ],
    "compact": [
        [1,1,1,1],
        [1,1,1,1],
        [1,1,1,1],
    ],
    "exam": [
        [1,0,1,0,1],
        [0,1,0,1,0],
        [1,0,1,0,1],
    ],
    "donut": [
        [0,1,1,1,0],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [0,1,1,1,0],
    ],
    "solo": [
        [1],
    ]
}

# Create your models here.
class Course(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    #basically, there can be more than 1 beadle and 1 professor for each course.
    courseUsers = models.ManyToManyField(settings.AUTH_USER_MODEL, through="CourseUser") 

    layout_type = models.CharField(
        max_length=50,
        choices=[
            ("lecture", "Lecture"),
            ("compact", "Compact"),
            ("exam", "Exam"),
            ("donut", "Donut"),
            ("solo", "Solo"),
        ],
        default="lecture"
    )

    layout = models.JSONField(default=list, blank=True)

    def save(self, *args, **kwargs):
        # autofill layout if not custom and layout is empty
        if self.layout_type != "custom": # and not self.layout:
            self.layout = LAYOUT_TEMPLATES.get(self.layout_type, [])
        super().save(*args, **kwargs)

    def generate_layout(self):
        if self.layout_type != "custom":
            return LAYOUT_TEMPLATES.get(self.layout_type, [])
        return self.layout

    def __str__(self):
        return '{}: {}'.format(self.code, self.name)

    def get_absolute_url(self):
        return reverse('courses:detail', args=[str(self.id)])
    
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

    def __str__(self):
        return self.user.fullname
    
    class Meta:
            constraints = [
        models.UniqueConstraint(fields=['user', 'course'], name='unique_user_course')
    ] #A user can't have 2 roles