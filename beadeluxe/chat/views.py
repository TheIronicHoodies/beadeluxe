from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from courses.models import CourseUser, Course
from .models import Message

# Create your views here.
class MessageView(LoginRequiredMixin, View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership:
            raise PermissionDenied

        messages = course.group_chat.all().order_by("timestamp")

        return render(request, "chat.html", {
            "messages": messages
        })

# class CreateMessageView(LoginRequiredMixin, View):
#     def post(self, request, course_id):
#         course = Course.objects.get(id=course_id)
#         membership = CourseUser.objects.filter(
#             user=request.user,
#             course=course
#         ).first()

#         if not membership or membership.role not in ["student", "beadle"]:
#             raise PermissionDenied
        
#         Message.objects.create(
#             course=course
#         )

#         return self.get(request, *args, **kwargs)