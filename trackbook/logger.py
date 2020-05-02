import json

import requests


class Logger:

    @staticmethod
    def debug(data):
        Logger.horn(json.dumps(data))

    @staticmethod
    def error(data):
        Logger.horn(json.dumps(data))

    @staticmethod
    def horn(data):
        data = {'text': data}
        requests.post("https://integram.org/webhook/cvKuVl40ZeZ", data=json.dumps(data))
