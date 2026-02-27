from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=46)
    nickname = models.CharField(max_length=20)
    pronounoptions = ["he/him", "she/her", "they/them", "he/they", "she/they", "other", "none"]
    pronouns = models.CharField(max_length=20, choices=[(option, option) for option in pronounoptions])
    email = models.EmailField(max_length=254)
    mobile_regex = RegexValidator(regex=r'^(\+\d{1,3})?,?\s?\d{8,13}$', message="Phone number must not consist of space and requires country code. eg : +6591258565")
    mobile_number = models.CharField(max_length=17, validators=[mobile_regex])
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    ROLE_CHOICES = [
        ("student", "Student"),
        ("beadle", "Beadle"),
        ("prof", "Professor"),
        ("admin", "Admin"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return self.fullname
    
    