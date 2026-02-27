from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from .models import Course
from .forms import CourseForm

# Create your views here.
# Class-based version
class CourseListView(ListView):
    model = Course
    template_name = 'course_list.html'

    def post(self, request, *args, **kwargs):
        c = Course()
        c.name = request.POST.get('course_name')
        c.code = request.POST.get('course_code')
        c.save()

        return self.get(request, *args, **kwargs)


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'


class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course_create.html'

    def post(self, request, *args, **kwargs):
        course_form = CourseForm(request.POST)
