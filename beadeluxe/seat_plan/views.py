import json, random
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.contrib import messages
from courses.models import CourseUser, Course
# from courses.forms import CourseLayoutForm
from .models import SeatAssignment
from django.core.exceptions import PermissionDenied

# Create your views here.

# create helper func to get user's membership in a course
def get_membership(user, course):
    return CourseUser.objects.filter(user=user, course=course).first()

# represents one seating arrangement
class SeatPlanView(LoginRequiredMixin, View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)
        membership = get_membership(request.user, course)

        # get all students and beadles
        students = CourseUser.objects.filter(
            course=course,
            role__in=["student", "beadle"]
        )

        assigned = SeatAssignment.objects.filter(course=course)

        # create dictionary where each (row, col) seat maps to the user assigned to it
        seat_map = {
            (a.row, a.col): a.course_user
            for a in assigned
        }

        layout = course.layout or []

        # matrix = []

        # for r, row_layout in enumerate(layout):
        #     row = []
        #     for c, seat_exists in enumerate(row_layout):
        #         if seat_exists:
        #             occupant = seat_map.get((r, c))
        #         else:
        #             occupant = None  # empty space
        #         row.append({
        #             "exists": seat_exists,
        #             "occupant": occupant
        #         })
        #     matrix.append(row)

        matrix = [
            [
                {
                    "exists": seat_exists,                                     # whether this seat exists in the layout
                    "occupant": seat_map.get((r, c)) if seat_exists else None  # who is sitting here (if seat exists)
                }
                for c, seat_exists in enumerate(row_layout)
            ]
            for r, row_layout in enumerate(layout)
        ]

        edit_mode = request.GET.get("edit_layout") == "1"

        return render(request, "seat_plan.html", {
            "seat_plan": matrix,
            "students": students,
            "assigned": assigned,
            "course": course,
            "user_role": membership.role,
            "user_course_id": membership.id,
            "edit_mode": edit_mode,
            # "form": CourseLayoutForm(instance=course),
        })

class UpdateSeatPlanView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)

        student_id = data.get("student_id")
        row = data.get("row")
        col = data.get("col")

        course_user = CourseUser.objects.get(id=student_id)
        course = course_user.course

        membership = get_membership(request.user, course)

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
        membership = get_membership(request.user, course_user.course)

        # students can only remove themselves
        if membership.role == "student" and str(student_id) != str(membership.id):
            raise PermissionDenied
            
        # remove seat
        SeatAssignment.objects.filter(course_user=course_user).delete()

        return JsonResponse({"status": "removed"})
    
class AutoAssignSeatsView(LoginRequiredMixin, View):
    def post(self, request, pk):
        course = Course.objects.get(pk=pk)
        membership = get_membership(request.user, course)

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        mode = request.POST.get("mode")

        # get list of students and beadles in course
        students = list(
            CourseUser.objects.filter(
                course=course,
                role__in=["student", "beadle"]
            ).select_related("user")
        )

        # get list of active seats
        seats = [
            (r, c)
            for r, row in enumerate(course.layout or [])
            for c, exists in enumerate(row)
            if exists
        ]

        # if there are most students than seats, send error message to template
        if len(students) > len(seats):
            messages.error(request, "Not enough seats for all students.")
            return redirect("courses:course_seat_plan", pk=pk)

        # choose ordering
        if mode == "random":
            random.shuffle(students)
        elif mode == "alphabetical":
            students.sort(
                key=lambda s: ( # sort by last name, then firstname
                    s.user.fullname.split()[-1].lower(),
                    s.user.fullname.lower()
                )
            )

        # clear existing assignments
        SeatAssignment.objects.filter(course=course).delete()

        # assign seats
        SeatAssignment.objects.bulk_create([
            SeatAssignment(
                course=course,
                course_user=student,
                row=r,
                col=c
            )
            for student, (r, c) in zip(students, seats)
        ])

        return redirect("courses:course_seat_plan", pk=pk)