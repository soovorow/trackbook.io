import datetime
import json

import requests

from trackbook.logger import Logger


class Facebook:

    @staticmethod
    def log_purchase(app, purchase):
        graph_version = 'v4.0'
        fb_app_id = app.fb_app_id
        url = f'https://graph.facebook.com/{graph_version}/{fb_app_id}/activities'
        access_token = Facebook.request_access_token(app)
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json',
        }

        purch_body = json.loads(purchase.request_body)
        purch_data = purch_body['data']
        fb = purch_data['fb']

        data = {
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
                "Product Title": purch_data['productTitle'],
                "fb_num_items": 1,
                "fb_content_type": "product",
                "fb_iap_product_type": "inapp",
                "_eventName": "fb_mobile_purchase",
            }]
        }
        request = requests.post(url, headers=headers, data=json.dumps(data))
        response = json.loads(request.text)
        is_logged = response['success']

        Logger.debug('Facebook Said: ' + str(response))
        return is_logged, response


    @staticmethod
    def request_access_token(app):

        token_request = requests.get(
            'https://graph.facebook.com/oauth/access_token' +
            '?client_id=' + app.fb_app_id +
            '&client_secret=' + app.fb_client_token +
            "&grant_type=client_credentials"
        )

        token_response = json.loads(token_request.text)
        access_token = token_response['access_token']
        return access_token
