from django.shortcuts import render
from .models import Course

# Create your views here.
# # Function-based version
def course_list(request):
    courses = Course.objects.all()
    ctx = {
        "courses": courses
    }

    return render(request, 'courses/course_list.html', ctx)

def course_detail(request, id):
    course = Course.objects.get(id=id)
    ctx = {'course' : Course.objects.get(id=id)}
    # ctx = {'course' : course}
    return render(request, 'courses/course_detail.html', ctx)


# Class-based version
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

# class CourseListView(ListView):
#     model = Course
#     template_name = 'courses/course_list.html'

# class CourseDetailView(DetailView):
#     model = Course
#     template_name = 'courses/course_detail.html'
