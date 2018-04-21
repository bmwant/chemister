import json
import operator

import yaml

import settings
from utils import get_logger
from crawler.scheduler import Scheduler
from crawler.factory import Factory


async def load_yaml(filepath):
    with open(filepath) as f:
        return yaml.load(f.read())


async def load_resources():
    data = await load_yaml(settings.RESOURCES_FILEPATH)
    return map(operator.itemgetter('name'), data)


async def get_cached_value(*, cache, key):
    value = await cache.get(key)
    if value is not None:
        return json.loads(value)


async def refresh_data():
    logger = get_logger()
    logger.info('Refreshing initiated from webapp')
    factory = Factory()
    await factory.init_cache()
    factory.load_resources()
    tasks = factory.create()
    scheduler = Scheduler(tasks=tasks)

    await scheduler.run_tasks()
    await scheduler.cleanup()
