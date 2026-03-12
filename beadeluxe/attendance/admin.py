from django.contrib import admin
from .models import Attendance, AttendanceSession

# Register your models here.
admin.site.register(Attendance)
admin.site.register(AttendanceSession)