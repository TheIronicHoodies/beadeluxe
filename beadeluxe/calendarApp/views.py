from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
import calendar
from datetime import datetime

from courses.models import Course, CourseUser
from .models import Event


import calendar
from datetime import datetime

import calendar
from datetime import datetime

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

        return render(request, "calendar.html", context)