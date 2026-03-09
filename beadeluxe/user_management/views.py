"""This file sets up the views for the user_management app."""
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import DetailView

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile
from .forms import ProfileForm, CustomUserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

class UserCreateView(CreateView):
    """
    Class for the User Create View.

    Contains the form for create a user.
    Creates a profile when a user is created.
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'user-management/profile_user_create.html'

    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()

        profile = Profile()
        profile.user = user
        profile.name = user.username
        profile.email = user.email
        profile.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if "email" in form.errors:
            form.add_error('email', "Email must be from @ateneo.edu or @student.ateneo.edu")
            return reverse_lazy('user_create')

class ProfileForbiddenView(TemplateView):
    """
    Class for the Profile Forbidden View
    """
    template_name = 'user-management/profile_forbidden.html'


class ProfileUpdateView(UpdateView, LoginRequiredMixin):
    """
    Class for the Profile Update View

    Contains the form to update the name of the profile of a user
    """
    model = Profile
    form_class = ProfileForm
    slug_field = "username__username"
    slug_url_kwarg = "username"
    template_name = 'user-management/profile_form.html'

    def get_success_url(self):
        return reverse_lazy('home')

    def get_object(self):

        object = get_object_or_404(User, username=self.kwargs.get("username"))

        if self.request.user.username == object.username:
            return object
        else:
            raise PermissionDenied
        
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = ProfileForm(instance=Profile.objects.get(user=self.get_object()))
        return ctx
    
    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=self.get_object())
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect(reverse('home'))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
        
class ProfileDetailView(DetailView):
    model = Profile
    template_name = "user-management/profile.html"
    slug_field = "user__username"        # field in your model
    slug_url_kwarg = "username"    # matches the URL pattern
