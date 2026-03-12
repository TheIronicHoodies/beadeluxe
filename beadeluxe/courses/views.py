from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth import get_user_model

from .models import Course, CourseUser

# Create your views here.
# Class-based version
class CourseListView(LoginRequiredMixin, ListView):
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
    
    def get_context_data(self, **kwargs):
        ctx = super(CourseListView, self).get_context_data(**kwargs)
        user = self.request.user
        ctx["object_list"] = CourseUser.objects.filter(user=user)
        return ctx


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = CourseUser
    template_name = 'course_detail.html'

    def post(self, request, *args, **kwargs):
        if request.POST.get("form_type") == "addMember":
            cu = CourseUser()
            cu.course = Course.objects.get(pk=self.kwargs.get('pk'))
            email = request.POST.get('email')
            cu.user = get_user_model().objects.get(email=email)
            cu.role = request.POST.get('role')
            cu.save()
        elif request.POST.get("form_type") == "assignBeadle":
            fullname = request.POST.get('fullname')
            course = Course.objects.get(pk=self.kwargs.get('pk'))
            user = get_user_model().objects.get(fullname=fullname)
            cu = CourseUser.objects.get(user=user, course=course)
            cu.role = "beadle"
            cu.save()
        elif request.POST.get("form_type") == "resign":
            user = self.request.user
            course = Course.objects.get(pk=self.kwargs.get('pk'))
            cu = CourseUser.objects.get(user=user, course=course)
            cu.role = "student"
            cu.save()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CourseDetailView, self).get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs.get('pk'))
        user = self.request.user
        ctx["object"] = CourseUser.objects.get(user=user, course=course)
        ctx["students"] = CourseUser.objects.filter(course=course, role='student')
        ctx["beadles"] = CourseUser.objects.filter(course=course, role='beadle')
        return ctx
