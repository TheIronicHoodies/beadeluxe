from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from courses.models import CourseUser, Course

# Create your views here.

# represents one seating arrangement
class SeatPlanView(LoginRequiredMixin, View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership:
            raise PermissionDenied

        # get all users in the course
        students = CourseUser.objects.filter(
            course=course
        )

        # create the seating matrix
        matrix = []
        for i in range(0, 4):
            row = [None, None, None, None, None, None, None, None]
            cols.append(row)

        return render(request, "seat_plan.html", {
            "course": course
        })
        
class UpdateSeatPlanView(LoginRequiredMixin, View):
    def post(self, request):
        if not course_user_id or not session_id:
            return redirect(request.META.get("HTTP_REFERER")) 

        course_user = CourseUser.objects.get(id=course_user_id)

        record, _ = Attendance.objects.get_or_create(
            course_user=course_user,
            session=session
        )

        return redirect(request.META.get("HTTP_REFERER"))
    