import json
import requests


class Apple:

    @staticmethod
    def verify_receipt(payload, bundle_id, product_id, transaction_id, is_sandbox = False):

        if is_sandbox:
            store = 'sandbox'
        else:
            store = 'buy'

        requestData = {'receipt-data': payload}
        response = requests.post('https://' + store + '.itunes.apple.com/verifyReceipt', data=json.dumps(requestData))
        response = json.loads(response.text)

        status = response['status']

        if status == 21007:
            return Apple.verify_receipt(payload, bundle_id, product_id, transaction_id, True)

        # start validation
        is_valid = False
        transaction_date = None

        if status != 0:
            return is_sandbox, is_valid, transaction_date

        receipt = response['receipt']

        if receipt['bundle_id'] != bundle_id:
            return is_sandbox, is_valid, transaction_date

        for p in receipt['in_app']:
            if p['product_id'] == product_id:
                if p['transaction_id'] == transaction_id:
                    is_valid = True
                    transaction_date = p['purchase_date']

        return is_sandbox, is_valid, transaction_date
