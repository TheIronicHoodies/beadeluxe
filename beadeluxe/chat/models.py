from django.db import models
from django.urls import reverse
from django.conf import settings
from courses.models import Course, CourseUser

# Create your models here.

# Represents one message
class Message(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="group_chat",
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        CourseUser,
        on_delete=models.CASCADE,
        related_name="student",
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    content = models.TextField(2048, null=False, blank=False)

    class Meta:
        unique_together = ("course", "timestamp")
    
    def __str__(self):
        return f"{self.course.code} - {self.user} - {self.timestamp}"
    
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