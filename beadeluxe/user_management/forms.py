from django import forms
from .models import Profile

"""This file sets up the forms for the user_management app."""
from django import forms
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    """
    Class for the Custom User Creation Form.

    Contains the fields 'email', 'username', 'password1' and 'password2' 
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    """
    Class for the Profile Form.

    Contains the field 'name'
    """
    class Meta:
        model = Profile
        fields = ['fullname', 'nickname', 'pronouns', 'email', 'mobile_number', 'profile_picture']