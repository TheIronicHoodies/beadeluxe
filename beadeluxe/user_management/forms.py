from django import forms
from .models import Profile

"""This file sets up the forms for the user_management app."""
from django import forms
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
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
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'pronouns': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

