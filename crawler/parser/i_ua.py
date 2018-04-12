from bs4 import BeautifulSoup

from crawler.parser import BaseParser, BaseEngine


class _BSEngine(BaseEngine):
    def process(self, html):
        soup = BeautifulSoup(html, 'html5lib')
        rows = soup.select('tbody tr')
        data = []
        for row in rows:
            cells = row.find_all('td')
            new_bid = {
                'rate': cells[1].text,
                'amount': cells[2].text,
                'phone': cells[3].text,
            }
            data.append(new_bid)

        self._data = data


class IUaParser(BaseParser):
    def __init__(self, engine_cls=_BSEngine):
        self.engine = engine_cls()

    def parse(self, html):
        self.engine.process(html)
        return self.engine.data
