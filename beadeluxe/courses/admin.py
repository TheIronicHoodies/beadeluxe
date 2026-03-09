from django.contrib import admin
from .models import Course, CourseUser

admin.site.register(Course)
admin.site.register(CourseUser)