from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
import calendar
from datetime import datetime

from courses.models import Course, CourseUser
from .models import Event


class CalendarView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership:
            raise PermissionDenied

        now = datetime.now()
        year = int(request.GET.get("year", now.year))
        month = int(request.GET.get("month", now.month))

        # FIX month overflow/underflow
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        month_name = calendar.month_name[month]
        cal = calendar.monthcalendar(year, month)

        events = Event.objects.filter(
            course=course,
            date__year=year,
            date__month=month
        )

        event_map = {}
        for event in events:
            event_map.setdefault(event.date.day, []).append(event)

        prev_month = month - 1
        prev_year = year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1

        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        context = {
            "course": course,
            "calendar": cal,
            "event_map": event_map,
            "month": month,
            "year": year,
            "prev_month": prev_month,
            "prev_year": prev_year,
            "next_month": next_month,
            "next_year": next_year,
            "role": membership.role,
            "month_name": month_name,
        }

        return render(request, "calendar/calendar.html", context)

class CreateEventView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        return render(request, "calendar/calendar_create_event.html", {
            "course": course
        })

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        title = request.POST.get("title")
        description = request.POST.get("description")
        date = request.POST.get("date")
        category = request.POST.get("category")

        if title and date and category:
            Event.objects.create(
                course=course,
                creator=request.user,
                title=title,
                description=description,
                date=date,
                category=category
            )

        return redirect("calendarApp:calendar", course.id)
    
class DeleteEventView(LoginRequiredMixin, View):
    def post(self, request, course_id, event_id):
        course = get_object_or_404(Course, id=course_id)

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        event = get_object_or_404(
            Event,
            id=event_id,
            course=course
        )

        event.delete()

        return redirect("calendarApp:calendar", course_id=course.id)
    
class EditEventView(LoginRequiredMixin, View):
    def get(self, request, course_id, event_id):
        course = get_object_or_404(Course, id=course_id)

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        event = get_object_or_404(
            Event,
            id=event_id,
            course=course
        )

        return render(request, "calendar/calendar_edit_event.html", {
            "event": event,
            "course": course
        })

    def post(self, request, course_id, event_id):
        course = get_object_or_404(Course, id=course_id)

        membership = CourseUser.objects.filter(
            user=request.user,
            course=course
        ).first()

        if not membership or membership.role != "beadle":
            raise PermissionDenied

        event = get_object_or_404(
            Event,
            id=event_id,
            course=course
        )

        event.title = request.POST.get("title")
        event.description = request.POST.get("description")
        event.date = request.POST.get("date")
        event.category = request.POST.get("category")
        event.save()

        return redirect("calendarApp:calendar", course.id)