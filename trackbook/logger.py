import json

import requests


class Logger:

    @staticmethod
    def horn(data):
        data = {'text': json.dumps(data)}
        requests.post("https://integram.org/webhook/cvKuVl40ZeZ", data=json.dumps(data))
