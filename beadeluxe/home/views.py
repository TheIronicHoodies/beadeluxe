from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.

class HomepageTemplateView(TemplateView):
    template_name = 'homepage.html'
