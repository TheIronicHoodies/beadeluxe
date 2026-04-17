from django import forms
from .models import Course

class CourseLayoutForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["layout_type"]  # only allow template selection