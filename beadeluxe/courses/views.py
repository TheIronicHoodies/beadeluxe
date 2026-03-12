from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView

from .models import Course, CourseUser
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

        #Whoever created the course is beadle
        if request.user.is_authenticated:
            cu = CourseUser()
            cu.course = c
            cu.user = request.user
            cu.role = "beadle"
            cu.save()
        return self.get(request, *args, **kwargs)


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course = self.object
        user = self.request.user

        membership = CourseUser.objects.filter(
            user=user,
            course=course
        ).first()

        context["membership"] = membership

        return context


class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'course_create.html'

    def post(self, request, *args, **kwargs):
        course_form = CourseForm(request.POST)
