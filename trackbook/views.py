import secrets

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views.generic.base import View

from trackbook.models import App


class HomeView(View):
    def get(self, request):
        return render(request, 'trackbook/home.html')


class SignUpView(View):
    def get(self, request):
        return render(request, 'trackbook/signup.html', {'form': UserCreationForm()})

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            return redirect(reverse('login'))

        return render(request, 'trackbook/signup.html', {'form': form})


class AppList(LoginRequiredMixin, ListView):
    template_name = 'trackbook/index.html'
    context_object_name = 'apps_list'
    paginate_by = 5

    def get_queryset(self):
        return App.objects.filter(user_id=self.request.user.id).order_by('-id')


class AppCreate(LoginRequiredMixin, CreateView):
    model = App
    fields = ['app_name', 'bundle_id', 'fb_app_id', 'fb_client_token']

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.created_at = timezone.now()
        form.instance.api_key = secrets.token_urlsafe(16)
        return super(AppCreate, self).form_valid(form)


class AppUpdate(LoginRequiredMixin, UpdateView):
    model = App
    fields = ['app_name', 'bundle_id', 'fb_app_id', 'fb_client_token']


class AppDetails(LoginRequiredMixin, DetailView):
    model = App
    template_name = 'trackbook/data.html'
