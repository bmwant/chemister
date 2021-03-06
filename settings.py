import os
from pathlib import Path


PROJECT_ROOT = Path(os.path.dirname(os.path.realpath(__file__)))
TEMPLATES_DIR = PROJECT_ROOT / 'templates'

REDIS_URI = 'redis://localhost'


DATABASE_DSN = 'postgres://username:password@127.0.0.1:5432/database'
TEST_DATABASE_DSN = 'postgres://username:password@127.0.0.1:5432/test_database'
DATABASE_POOL_MINSIZE = 3
DATABASE_POOL_MAXSIZE = 10

APPLY_FILTER = True
DEFAULT_UPDATE_PERIOD = 5  # update interval in minutes

RESOURCES_FILEPATH = PROJECT_ROOT / 'resources.yml'

GECKO_DRIVER_PATH = PROJECT_ROOT / 'lib' / 'geckodriver'
CHROME_DRIVER_PATH = PROJECT_ROOT / 'lib' / 'chromedriver'


HEALTHCHECK_ENDPOINT = None

DEFAULT_DATE_FORMAT = '%d/%m/%y'
DEFAULT_TIME_FORMAT = '%H:%M'
DEFAULT_DATETIME_FORMAT = '{} {}'.format(DEFAULT_TIME_FORMAT,
                                         DEFAULT_DATE_FORMAT)

SYSTEM_USER_ID = 0

# NOTIFICATIONS
ENDPOINT_TEMPLATE = 'https://api.telegram.org/bot{bot_api_key}/sendMessage'
TELEGRAM_BOT_TOKEN = None  # required, override via env or settings_local.py
CHAT_ID = None  # required, override via env or settings_local.py

# AIOHTTP
FLASH_SESSION_KEY = 'flash'
FLASH_REQUEST_KEY = 'flash'

# DEVELOPING
DEBUG = False
DEV_BID_RESOURCE = PROJECT_ROOT / 'resources' / 'bids.yml'
SESSION_SECRET_KEY = 'P-mbeuEe5XtZL7lBJQfsm5EtOxWB3CWH3G4lmf4ELcM='

# Override values from settings_local.py
try:
    import settings_local
    for key, value in settings_local.__dict__.items():
        if key.isupper() and key in globals():
            globals()[key] = value
except ImportError:
    pass

# Override values from environment
for key, value in globals().copy().items():
    if key.isupper() and key in os.environ:
        globals()[key] = os.environ[key]
