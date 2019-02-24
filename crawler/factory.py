"""
Create `Grabber` instances for list of resources we need to grab information
from.
"""
import importlib

import yaml

import settings
from utils import get_logger
from crawler.models.resource import Resource
from crawler.scheduled_task import ScheduledTask
from crawler.proxy import Proxy
from crawler.cache import Cache
from crawler.db import get_engine

# what?
from trader.shift_trader import ShiftTrader_v0


class Factory(object):
    def __init__(self, resources=None):
        self.resources = resources or []
        self.cache = None
        self.logger = get_logger(self.__class__.__name__.lower())

    def load_resources(self):
        self.logger.debug('Loading resources..')
        with open(settings.RESOURCES_FILEPATH) as f:
            resources = yaml.load(f.read())
        self.resources = [Resource(**r) for r in resources]
        return self.resources

    async def init_cache(self):
        """
        One shared instance for cache, but also may be implemented in the same
        way as database engine.
        """
        self.logger.debug('Initializing cache...')
        self.cache = Cache()
        await self.cache._create_pool()

    async def init(self):
        self.load_resources()
        await self.init_cache()

    async def cleanup(self):
        self.logger.debug('Closing factory resources...')
        await self.cache.close()

    def _load_cls_from_module(self, subpackage, module_name):
        """
        Load class from module name which follows our naming conventions.
        """
        full_module_name = f'{__package__}.{subpackage}.{module_name}'
        try:
            module = importlib.import_module(full_module_name)
        except ModuleNotFoundError:
            raise ValueError(
                f'No such {subpackage}: {full_module_name}. '
                f'Check resources file syntax.'
            )

        class_name = f'{module_name}_{subpackage}'.title().replace('_', '')
        cls_obj = getattr(module, class_name, None)
        if cls_obj is None:
            raise ValueError(
                f'No such class {class_name} '
                f'within module {full_module_name}.'
            )

        return cls_obj

    def get_parser(self, parser_name):
        parser_cls = self._load_cls_from_module('parser', parser_name)
        return parser_cls()

    def get_fetcher(self, resource):
        fetcher_cfg = resource.fetcher
        proxy_cfg = resource.proxy
        fetcher_name = fetcher_cfg.instance
        driver_name = fetcher_cfg.driver

        proxy = None
        if proxy_cfg.use:
            proxy = Proxy(ip=resource.proxy.ip, port=resource.proxy.port)

        driver_cls = None
        if driver_name:
            driver_cls = self._load_cls_from_module('driver', driver_name)

        fetcher_cls = self._load_cls_from_module('fetcher', fetcher_name)
        return fetcher_cls(
            base_url=None,
            proxy=proxy,
            driver_cls=driver_cls,
        )

    def get_grabber(self, resource, *, fetcher, parser, cache, engine):
        grabber_name = resource.grabber
        grabber_cls = self._load_cls_from_module('grabber', grabber_name)
        return grabber_cls(
            resource=resource,
            fetcher=fetcher,
            parser=parser,
            cache=cache,
            engine=engine,
        )

    async def create_grabbers(self):
        grabbers = []
        # Each grabber is responsible for closing resources within itself
        for res in self.resources:
            fetcher = self.get_fetcher(res)
            parser = self.get_parser(res.parser)
            engine = await get_engine()
            grabber = self.get_grabber(
                resource=res,
                fetcher=fetcher,
                parser=parser,
                cache=self.cache,
                engine=engine,
            )
            grabbers.append(grabber)
        return grabbers

    async def create_traders(self):
        # Create multiple traders for different algorithms
        # todo: reuse cache from here
        trader = ShiftTrader_v0(
            starting_amount=10000,
            shift=6,
        )
        await trader.init()
        return [
            ScheduledTask(
                task=trader.daily,
                scheduled_time='09:00',
            )
        ]

    async def create_daily(self):
        return []
