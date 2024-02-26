import logging
import os
from dotenv import load_dotenv
from logging.config import dictConfig


load_dotenv()

DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)-10s] %(module)-15s: %(message)s'
        },
        'standard': {
            'format': '%(name)-15s [%(levelname)-10s] %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/logs.log',
            'formatter': 'verbose'
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'verbose'
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'logs/error.log',
            'formatter': 'verbose'
        }
    },
    "loggers":{
        "bot": {
            'handlers': ['debug'],
            "level": 'INFO',
            "propagate": False
        },
        'discord': {
            'handlers': ["file", 'error'],
            'level': "INFO",
            'formatter': 'verbose',
            'propagate': True
        }
    }
}

dictConfig(LOGGING_CONFIG)