import datetime
import hashlib
import json
import secrets
import logging
import urllib
from json import JSONDecodeError

import requests
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.views.generic.base import View

from trackbook.forms import UploadFileForm
from trackbook.logger import Logger
from trackbook.models import App, Purchase
from trackbook.services.apple import Apple
from trackbook.services.facebook import Facebook


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
        form.instance.api_key = secrets.token_urlsafe(32)
        return super(AppCreate, self).form_valid(form)


class AppUpdate(LoginRequiredMixin, UpdateView):
    model = App
    fields = ['app_name', 'bundle_id', 'fb_app_id', 'fb_client_token']


class AppDetails(LoginRequiredMixin, DetailView):
    model = App
    template_name = 'trackbook/data.html'


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@method_decorator(csrf_exempt, name='dispatch')
class LogEvent(View):
    http_method_names = ['post']

    def post(self, request):
        # Is request encoding valid?
        try:
            body = request.body.decode('utf-8')
            body = json.loads(body)
        except Exception:
            ip = get_client_ip(request)
            Logger.error(ip + " " + request.body)
            Logger.error(f'Warning. {ip} trying to push invalid data.', True)
            return JsonResponse({'status': 'error', 'message': 'Decoding error. Invalid data.'})

        # Is request authenticated?
        try:
            auth = request.headers['Authorization'].split(' ')[1].split(':')
            app_id = auth[0]
            api_key = auth[1]
            app = App.objects.get(id=app_id, api_key=api_key)
        except Exception:
            Logger.horn('Warning. Somebody trying to log with unauthorized access.')
            return JsonResponse({'status': 'error', 'message': 'Unauthorized access'})

        # Is IOS platform?
        if 'platform' not in body:
            return JsonResponse({'status': 'error', 'message': 'platform is not set.'})
        if body['platform'] != 'ios':
            return JsonResponse({'status': 'error', 'message': 'requested platform is not supported.'})

        # Are valid keys in request?
        try:
            transactionID = body['data']['transaction_id']
            advertiser_id = body['data']['advertiser_id']
            product_id = body['data']['product_id']
            price_sum = body['data']['valueToSum']
            currency = body['data']['currency']
            bundle_short_version = body['data']['bundleShortVersion']
            payload = body['data']['receipt_data']
            extinfo = body['data']['fb']['extinfo']
        except KeyError:
            Logger.horn('Warning. Somebody with access token trying to push incorrect key-value data.')
            return JsonResponse({'status': 'error', 'message': 'Incorrect key-value format.'})

        # Is purchase in database?
        try:
            Purchase.objects.get(transaction_id=transactionID)
            Logger.error('Transaction already logged. Maybe there an issue with lost transactions', True)
            return JsonResponse({'status': 'error', 'message': 'Transaction already logged.'})
        except Purchase.DoesNotExist:
            pass

        # Create purchase record
        purchase = Purchase()
        purchase.app_id = app.id
        purchase.transaction_id = transactionID
        purchase.advertiser_id = advertiser_id
        purchase.bundle_short_version = bundle_short_version
        purchase.product_id = product_id
        purchase.ext_info = json.dumps(extinfo)
        purchase.sum = price_sum
        purchase.currency = currency
        purchase.request_body = json.dumps(body)
        purchase.log_timestamp = int(datetime.datetime.now().timestamp())
        purchase.save()

        # Is apple receipt validation passed?
        try:
            is_sandbox, is_valid, transaction_date = Apple.verify_receipt(
                payload,
                app.bundle_id,
                purchase.product_id,
                purchase.transaction_id
            )
        except Exception:
            Logger.error(str(Exception))
            Logger.error('Alarm. Apple verification service is not available.', True)
            return JsonResponse({'status': 'warning', 'message': 'Apple verification service is not available'})

        if is_valid:
            purchase.is_sandbox = is_sandbox
            purchase.transaction_date = transaction_date
            purchase.is_valid = 1
            purchase.save()
        else:
            purchase.transaction_id = "fake_" + purchase.transaction_id
            purchase.save()
            Logger.error('Info. Somebody trying to push fake purchase. Don\'t worry, I handle it.', True)
            return JsonResponse({'status': 'error', 'message': 'Fake receipt.'})

        if 'log_any' not in body and purchase.is_sandbox:
            return JsonResponse({'status': 'success', 'purchase': purchase.as_json() })

        # Log Facebook Event
        try:
            is_logged, log_response = Facebook.log_purchase(app, purchase)
        except Exception:
            Logger.error('Alarm. Facebook purchase log throw exception: ' + str(Exception), True)
            return JsonResponse({'status': 'error', 'message': 'Facebook log goes wrong'})

        if is_logged:
            purchase.is_logged = 1
            purchase.save()

            horn = "💰 +" + str(purchase.sum) + purchase.currency + " \n"
            horn += "\"" + body['data']['productTitle'] + " (v" + purchase.bundle_short_version + ")"
            Logger.horn(horn)

        return JsonResponse({'status': 'success', 'purchase': purchase.as_json()})


@method_decorator(csrf_exempt, name='dispatch')
class LogDebug(View):
    http_method_names = ['post']

    def post(self, request):

        # Is request authenticated?
        try:
            auth = request.headers['Authorization'].split(' ')[1].split(':')
            app_id = auth[0]
            api_key = auth[1]
            app = App.objects.get(id=app_id, api_key=api_key)
        except Exception:
            Logger.horn('Warning. Somebody trying to log with unauthorized access.')
            return JsonResponse({'status': 'error', 'message': 'Unauthorized access'})

        # Is request valid?
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            dt = str(datetime.datetime.now()).replace(' ', '_')
            with open(f'/var/www/trackbook.io/uploads/{dt}.txt', 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            return JsonResponse({'status': 'success', 'message': 'file saved'})
        else:
            Logger.error('Warning. Somebody trying to send invalid debug log.')
            return JsonResponse({'status': 'error', 'message': 'Decoding error. Invalid data.'})


