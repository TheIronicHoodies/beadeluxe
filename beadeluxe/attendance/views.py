from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from courses.models import CourseUser
from .models import Attendance

# Create your views here.

@login_required
def attendance_view(request):

    user = request.user

    # Get all courses enrolled for this user
    enrollments = CourseUser.objects.filter(user=user)

    attendance_data = []

    for enrollment in enrollments:
        records = Attendance.objects.filter(course_user=enrollment)

        total_classes = records.count()

        cuts = records.filter(status="absent").count()
        lates = records.filter(status="late").count()

        # Make lates count as half-cut
        cuts = cuts + (lates * 0.5)

        attendance_data.append({
            "course": enrollment.course,
            "records": records,
            "cuts": cuts,
            "total_classes": total_classes
        })

    

    context = {
        "attendance_data": attendance_data
    }

    return render(request, "attendance.html", context)