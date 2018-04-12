import re

from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def parse(self, html):
        pass


class BaseEngine(ABC):
    def __init__(self):
        self._data = {}

    @staticmethod
    def find_tag(tag_name, html_data):
        exp = '<{tag_name}[^>]*>(.*?)</{tag_name}>'.format(tag_name=tag_name)
        m = re.search(exp, html_data)
        result = m.group(1)  # Match within a tag
        return result

    @abstractmethod
    def process(self, html):
        pass

    @property
    def data(self):
        return self._data
