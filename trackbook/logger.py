import json
import logging
import requests


class Logger:

    @staticmethod
    def debug(data, horn=False):
        logger = logging.getLogger('django')
        logger.debug(data)
        if horn:
            try:
                Logger.horn(json.dumps(data))
            except:
                pass

    @staticmethod
    def error(data, horn=False):
        logger = logging.getLogger('django')
        logger.error(data)
        if horn:
            try:
                Logger.horn(json.dumps(data))
            except:
                pass

    @staticmethod
    def horn(data):
        data = {'text': data}
        requests.post("https://integram.org/webhook/cvKuVl40ZeZ", data=json.dumps(data))
