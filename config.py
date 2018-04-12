import os
from pathlib import Path


PROJECT_ROOT = Path(os.path.dirname(os.path.realpath(__file__)))
TEMPLATES_DIR = PROJECT_ROOT / 'templates'

REDIS_URI = 'redis://localhost'

UPDATE_PERIOD = 5 * 60  # 5 mins update interval

TEAMS_FILEPATH = PROJECT_ROOT / 'teams.yml'
RESOURCES_FILEPATH = PROJECT_ROOT / 'resources.yml'

GECKO_DRIVER_PATH = PROJECT_ROOT / 'lib' / 'geckodriver'
CHROME_DRIVER_PATH = PROJECT_ROOT / 'lib' / 'chromedriver'
