import os
from pathlib import Path


PROJECT_ROOT = Path(os.path.dirname(os.path.realpath(__file__)))
TEMPLATES_DIR = PROJECT_ROOT / 'templates'

REDIS_URI = 'redis://localhost'


DATABASE_DSN = 'postgres://username:password@127.0.0.1:5432/database'
DATABASE_POOL_MINSIZE = 3
DATABASE_POOL_MAXSIZE = 10

UPDATE_PERIOD = 5 * 60  # 5 mins update interval

RESOURCES_FILEPATH = PROJECT_ROOT / 'resources.yml'

GECKO_DRIVER_PATH = PROJECT_ROOT / 'lib' / 'geckodriver'
CHROME_DRIVER_PATH = PROJECT_ROOT / 'lib' / 'chromedriver'

## DEVELOPING
DEV_BID_RESOURCE = PROJECT_ROOT / 'resources' / 'bids.yml'


# Override values from config_local.py
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
