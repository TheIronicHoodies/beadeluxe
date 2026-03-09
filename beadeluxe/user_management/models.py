from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator   

class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=46)
    nickname = models.CharField(max_length=20)
    pronounoptions = [
        ("he/him", "he/him"),
        ("she/her", "she/her"),
        ("they/them", "they/them"),
        ("he/they", "he/they"),
        ("she/they", "she/they"),
        ("other", "other"),
        ("none", "none"),
    ]
    pronouns = models.CharField(max_length=20, choices=pronounoptions)
    mobile_regex = RegexValidator(
        regex=r'^(\+\d{1,3})?,?\s?\d{8,13}$',
        message="Phone number must not consist of space and requires country code. eg : +6591258565"
    )
    mobile_number = models.CharField(max_length=17, validators=[mobile_regex])
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.fullname

    
    
