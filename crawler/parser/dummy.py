from crawler.parser import BaseParser


__all__ = (
    'DummyParser',
)


class DummyParser(BaseParser):
    def parse(self, html):
        return {}
