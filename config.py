import logging
from os import environ, path
from dotenv import load_dotenv


class ProjectConfig(object):
    def __init__(self, **kwargs):
        # set default values
        self._dict = {
            # pc config
            'IP_ADDRESS': 'localhost',
            'IP_PORT': 9999,
            # usb config
            'USB_PORT': '/dev/ttyACM0',
            'USB_BAUD_RATE': 115200,
            # log config
            'LOG_LEVEL': logging.INFO,
            'LOG_FORMAT': '%(asctime)s - %(message)s',
            'LOG_FILE': 'app.log',
            'LOG_MODE': 'a',
        }
        self.load()
        self._dict.update(kwargs)

    def load(self):
        # Find and load .env file
        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))
        # update the dict
        self._dict.update(environ.items())

    def get(self, key: str):
        return self._dict.get(key)
