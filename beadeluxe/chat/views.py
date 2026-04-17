from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import View
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from courses.models import CourseUser, Course
from .models import Message

# Create your views here.
class MessageView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
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

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role not in ["student", "beadle"]:
            raise PermissionDenied
        
        Message.objects.create(
            user=membership,
            course=course,
            content=request.POST.get("content"),
            timestamp=request.POST.get("timestamp")
        )

        return self.get(request, course_id)