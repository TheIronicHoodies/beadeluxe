import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from courses.models import CourseUser, Course
from .models import SeatAssignment
from django.core.exceptions import PermissionDenied

# Create your views here.

# represents one seating arrangement
class SeatPlanView(LoginRequiredMixin, View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        # if membership.role not in ["beadle", "professor"]:
        #     raise PermissionDenied

        # get all users in the course
        # students = CourseUser.objects.filter(
        #     course=course
        # )

        # get all students and beadles
        students = CourseUser.objects.filter(
            course=course,
            role__in=["student", "beadle"]
        )

        assigned = SeatAssignment.objects.filter(course=course)
        assigned_ids = assigned.values_list("course_user_id", flat=True)

        # create dictionary where each (row, col) seat maps to the user assigned to it
        seat_map = {
            (a.row, a.col): a.course_user
            for a in assigned
        }

        matrix = []

        # 5x8 seatplan matrix based on dictionary
        for r in range(5):
            row = []
            for c in range(8):
                occupant = seat_map.get((r, c))
                row.append(occupant) # will be None if no occupant
            matrix.append(row)

        return render(request, "seat_plan.html", {
            "seat_plan": matrix,
            "students": students,
            "assigned": assigned,
            "course": course,
            "user_role": membership.role,
            "user_course_id": membership.id,
        })

class UpdateSeatPlanView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)

        student_id = data.get("student_id")
        row = data.get("row")
        col = data.get("col")

        course_user = CourseUser.objects.get(id=student_id)
        course = course_user.course

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        # students can only move themselves
        if membership.role == "student" and str(student_id) != str(membership.id):
            raise PermissionDenied

        # prevent them taking an occupied seat
        existing = SeatAssignment.objects.filter(
            course=course,
            row=row,
            col=col
        ).first()

        if existing and existing.course_user != course_user:
            raise PermissionDenied

        # remove previous seat (if any)
        SeatAssignment.objects.filter(course_user=course_user).delete()

        # assign new seat
        SeatAssignment.objects.create(
            course=course,
            course_user=course_user,
            row=row,
            col=col
        )

        return JsonResponse({"status": "ok"})
    
class RemoveSeatAssignmentView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        
        student_id = data.get("student_id")
        course_user = CourseUser.objects.get(id=student_id)
        membership = CourseUser.objects.filter(
            user=request.user,
            course=course_user.course
        ).first()

        # students can only remove themselves
        if membership.role == "student" and str(student_id) != str(membership.id):
            raise PermissionDenied
            
        # remove seat
        SeatAssignment.objects.filter(course_user=course_user).delete()

        return JsonResponse({"status": "removed"})