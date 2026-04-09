from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from courses.models import Course, CourseUser
from .models import Announcement


class AnnouncementView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership:
            raise PermissionDenied
        
        if membership.role.lower() == "professor":
            raise PermissionDenied

        announcements = course.announcements.all()

        return render(
            request,
            "announcements/announcements.html",
            {
                "course": course,
                "announcements": announcements,
                "role": membership.role,
            }
        )


class CreateAnnouncementView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        return render(
            request,
            "announcements/announcement_create.html",
            {"course": course}
        )

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        title = request.POST.get("title")
        content = request.POST.get("content")

        if title and content:
            Announcement.objects.create(
                course=course,
                author=request.user,
                title=title,
                content=content
            )

        return redirect("announcements:announcement_list", course.id)


class DeleteAnnouncementView(LoginRequiredMixin, View):
    def post(self, request, course_id, announcement_id):
        announcement = get_object_or_404(
            Announcement,
            id=announcement_id,
            course_id=course_id
        )

        membership = CourseUser.objects.filter(
            user=request.user,
            course_id=course_id
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        announcement.delete()

        return redirect(
            "announcements:announcement_list",
            course_id=course_id
        )


class EditAnnouncementView(LoginRequiredMixin, View):
    def get(self, request, course_id, announcement_id):
        announcement = get_object_or_404(
            Announcement,
            id=announcement_id,
            course_id=course_id
        )

        membership = CourseUser.objects.filter(
            user=request.user,
            course_id=course_id
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        return render(
            request,
            "announcements/announcement_edit.html",
            {
                "announcement": announcement,
                "course": announcement.course
            }
        )

    def post(self, request, course_id, announcement_id):
        announcement = get_object_or_404(
            Announcement,
            id=announcement_id,
            course_id=course_id
        )

        membership = CourseUser.objects.filter(
            user=request.user,
            course_id=course_id
        ).first()

        if not membership or membership.role not in ["beadle", "professor"]:
            raise PermissionDenied

        announcement.title = request.POST.get("title")
        announcement.content = request.POST.get("content")
        announcement.save()

        return redirect(
            "announcements:announcement_list",
            course_id=course_id
        )