import os
import datetime as dt

MAJOR = 1
MINOR = 0
PATCH = 0

APP_NAME = 'coinbot'
APP_AUTHOR = ' Dmitri McGuckin'
APP_DESCRIPTION = 'A simple wallet monitor and general-purpose coin-ticker' \
                  ' for various crypto-currencies'
APP_VERSION = f'{MAJOR}.{MINOR}.{PATCH}'
APP_LICENSE = 'GPL-3.0'
APP_URL = 'https://github.com/dmitri-mcguckin/coinbase-monitor'

API_UPDATE_INTERVAL = dt.timedelta(seconds=10)
# API_UPDATE_INTERVAL = dt.timedelta(minutes=1)

CACHE_DIR = os.path.expanduser('~/.cache/coinbot')
ACCOUNTS = f'{CACHE_DIR}/accounts.json'
PRICE_HISTORY_DB = f'{CACHE_DIR}/price_history.db'
