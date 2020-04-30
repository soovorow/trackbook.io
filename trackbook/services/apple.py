import json
import requests

from trackbook.logger import Logger


class Apple:

    @staticmethod
    def verify_receipt(env, payload):

        if env:
            store = 'buy'
        else:
            store = 'sandbox'

        requestData = {'receipt-data': payload}
        response = requests.post('https://' + store + '.itunes.apple.com/verifyReceipt', data=json.dumps(requestData))
        response = json.loads(response.text)
        Logger.debug(response)

        receipt = None
        status = response['status']

        if status == 21007:
            return Apple.verify_receipt(False, payload)

        if status == 0:
            receipt = response['receipt']

        return env, status, receipt
