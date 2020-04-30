import datetime
import json
import secrets
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

from trackbook.models import App, Purchase


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


@method_decorator(csrf_exempt, name='dispatch')
class LogEvent(View):
    http_method_names = ['post']

    def post(self, request):

        # Is request encoding valid?
        try:
            body = request.body.decode('utf-8')
            body = json.loads(body)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Decoding error. Invalid data.'})

        # Is request authenticated?
        try:
            auth = request.headers['Authorization'].split(' ')[1].split(':')
            app_id = auth[0]
            api_key = auth[1]
            app = App.objects.get(id=app_id, api_key=api_key)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized access'})

        # Is IOS platform?
        if 'platform' not in body:
            return JsonResponse({'status': 'error', 'message': 'platform is not set.'})
        if body['platform'] != 'ios':
            return JsonResponse({'status': 'error', 'message': 'requested platform is not supported.'})

        # Are valid keys in request?
        try:
            is_sandbox = int(body['data']['isSandbox'])
            transactionID = body['data']['transaction_id']
            advertiser_id = body['data']['advertiser_id']
            product_id = body['data']['product_id']
            price_sum = body['data']['valueToSum']
            currency = body['data']['currency']
            bundle_short_version = body['data']['bundleShortVersion']
            payload = body['data']['receipt_data']
        except KeyError:
            return JsonResponse({'status': 'error', 'message': 'Incorrect key-value format.'})

        # Is purchase in database?
        try:
            purchase = Purchase.objects.get(transaction_id=transactionID)
        except Purchase.DoesNotExist:
            purchase = Purchase()
            purchase.app_id = app.id
            purchase.is_sandbox = is_sandbox
            purchase.transaction_id = transactionID
            purchase.advertiser_id = advertiser_id
            purchase.bundle_short_version = bundle_short_version
            purchase.product_id = product_id
            purchase.sum = price_sum
            purchase.currency = currency
            purchase.request_body = json.dumps(body)
            purchase.log_timestamp = int(datetime.datetime.now().timestamp())
            purchase.save()

        # Is purchase already logged?
        if purchase.is_logged == 1:
            return JsonResponse({'status': 'error', 'message': 'Transaction already logged.'})

        # Is apple receipt validation passed?
        isValidPurchase = False
        b = json.loads(purchase.request_body)
        payload = b['data']['receipt_data']
        requestData = {'receipt-data': payload}
        env = 'buy'
        if purchase.is_sandbox: env = 'sandbox'

        try:
            r = requests.post("https://" + env + ".itunes.apple.com/verifyReceipt", data=json.dumps(requestData))
            response = json.loads(r.text)
            print(response)
            status = response['status']
            receipt = response['receipt']
        except KeyError:
            return JsonResponse({'status': 'error', 'message': 'Wrong environment or Apple verification service is '
                                                                 'not available'})

        if status != 0:
            return JsonResponse({'status': 'error', 'message': 'Invalid receipt.'})

        if receipt['bundle_id'] != app.bundle_id:
            return JsonResponse({'status': 'error', 'message': 'Fake receipt.'})

        in_app = receipt['in_app']
        for p in in_app:
            if p['product_id'] == purchase.product_id:
                if p['transaction_id'] == purchase.transaction_id:
                    isValidPurchase = True
                    purchase.transaction_date = p['purchase_date']

        if not isValidPurchase:
            return JsonResponse({'status': 'error', 'message': 'Fake receipt'})

        purchase.is_valid = 1
        purchase.save()

        # Is Sandbox Request?
        if purchase.is_sandbox:
            return JsonResponse({
                'status': 'success',
                'purchase': purchase.as_json()
            })

        # Log Facebook Event
        fb = b['data']['fb']

        token_request = requests.get('https://graph.facebook.com/oauth/access_token'
                                     '?client_id=' + app.fb_app_id +
                                     '&client_secret=' + app.fb_client_token +
                                     "&grant_type=client_credentials")
        token_response = json.loads(token_request.text)
        fb_access_token = token_response['access_token']

        fb_graph_version = 'v4.0'
        fb_app_id = app.fb_app_id
        headers = {
            'Authorization': 'Bearer ' + fb_access_token,
            'Content-Type': 'application/json',
        }
        facebookData = {
            'event': 'CUSTOM_APP_EVENTS',
            'advertiser_id': purchase.advertiser_id,
            'bundle_version': purchase.bundle_short_version,
            'bundle_short_version': purchase.bundle_short_version,
            'app_user_id': fb['user_id'],
            'advertiser_tracking_enabled': fb['advertiser_tracking_enabled'],
            'application_tracking_enabled': fb['application_tracking_enabled'],
            'extinfo': fb['extinfo'],
            'custom_events': [{
                "_logTime": int(datetime.datetime.now().timestamp()),
                "fb_transaction_date": purchase.transaction_date,
                "Transaction Identifier": purchase.transaction_id,
                "fb_content": [{"id": purchase.product_id, "quantity": 1}],
                "_valueToSum": purchase.sum,
                "fb_currency": purchase.currency,
                "Product Title": b['data']['productTitle'],
                "fb_num_items": 1,
                "fb_content_type": "product",
                "fb_iap_product_type": "inapp",
                "_eventName": "fb_mobile_purchase",
            }]
        }

        print(json.dumps(facebookData))

        log_request = requests.post('https://graph.facebook.com/' + fb_graph_version + '/' + fb_app_id + '/activities',
                                    data=json.dumps(facebookData), headers=headers)
        log_response = json.loads(log_request.text)

        print('Facebook Said: ' + str(log_response))

        if log_response['success']:
            purchase.is_logged = 1
            purchase.save()

        return JsonResponse({
            'status': 'success',
            'purchase': purchase.as_json()
        })
