import logging
from os import environ, path
from dotenv import load_dotenv


class ProjectConfig(object):
    def __init__(self, default=True, **kwargs):
        self._dict = {}
        # set default values
        if default:
            self._dict = {
                # pc config
                'IP_ADDRESS': 'localhost',
                'IP_PORT': 9000,
                # usb config
                'USB_PORT': '/dev/ttyACM0',
                'USB_BAUD_RATE': 115200,
            }
        else:
            self.load_from_env()
        self._dict.update(kwargs)

    def load_from_env(self):
        # Find and load .env file
        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))
        # update the dict
        self._dict.update(environ.items())

    def get(self, key: str):
        return self._dict.get(key)
