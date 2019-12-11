import secrets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView, UpdateView, DetailView, ListView

from divineog.models import App


class IndexView(LoginRequiredMixin, ListView):
    template_name = 'divineog/index.html'
    context_object_name = 'apps_list'
    paginate_by = 5

    def get_queryset(self):
        return App.objects.filter(user_id=self.request.user.id).order_by('-id')


class AppCreate(LoginRequiredMixin, CreateView):
    model = App
    fields = ['platform', 'app_name', 'bundle_id', 'fb_app_id', 'fb_client_token']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.created_at = timezone.now()
        form.instance.api_key = secrets.token_urlsafe(16)
        return super(AppCreate, self).form_valid(form)


class AppUpdate(LoginRequiredMixin, UpdateView):
    model = App
    fields = ['platform', 'app_name', 'bundle_id', 'fb_app_id', 'fb_client_token']


class AppDetails(LoginRequiredMixin, DetailView):
    model = App
    template_name = 'divineog/data.html'
