"""This file sets up the views for the user_management app."""
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProfileForm, CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

User = get_user_model()
class UserCreateView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'user-management/profile_user_create.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        if "email" in form.errors:
            form.add_error('email', "Email must be from @ateneo.edu or @student.ateneo.edu")
        return super().form_invalid(form)



class ProfileForbiddenView(TemplateView):
    """
    Class for the Profile Forbidden View
    """
    template_name = 'user-management/profile_forbidden.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm   # should be a ModelForm for CustomUser
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'user-management/profile_form.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        if self.request.user.username == user.username:
            return user
        else:
            raise PermissionDenied
        
class ProfileDetailView(DetailView):
    model = User
    template_name = "user-management/profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['profile'] = self.object 
        return ctx


