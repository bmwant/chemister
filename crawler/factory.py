"""
Create `Grabber` instances for list of resources we need to grab information
from.
"""
import importlib

import yaml

import settings
from utils import get_logger
from crawler.models.resource import Resource
from crawler.proxy import Proxy
from crawler.cache import Cache


class Factory(object):
    def __init__(self, resources=None, teams=None):
        self.resources = resources or []
        self.teams = teams or []
        self.cache = None
        self.logger = get_logger(self.__class__.__name__.lower())

    def load_resources(self):
        self.logger.debug('Loading resources..')
        with open(settings.RESOURCES_FILEPATH) as f:
            resources = yaml.load(f.read())
        self.resources = [Resource(**r) for r in resources]

    async def init_cache(self):
        self.logger.debug('Initializing cache...')
        self.cache = Cache()
        await self.cache._create_pool()

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

    def get_grabber(self, resource, *, fetcher, parser, cache):
        grabber_name = resource.grabber
        grabber_cls = self._load_cls_from_module('grabber', grabber_name)
        return grabber_cls(
            resource=resource,
            fetcher=fetcher,
            parser=parser,
            cache=cache,
        )

    def create(self):
        grabbers = []
        for res in self.resources:
            fetcher = self.get_fetcher(res)
            parser = self.get_parser(res.parser)
            grabber = self.get_grabber(
                resource=res,
                fetcher=fetcher,
                parser=parser,
                cache=self.cache,
            )
            grabbers.append(grabber)
        return grabbers
