from bs4 import BeautifulSoup

from crawler.parser import BaseParser, BaseEngine


class _BSEngine(BaseEngine):
    def process(self, html):
        html = html.replace('<!---->', '')
        soup = BeautifulSoup(html, 'html5lib')
        items = soup.find_all('div', 'outright-item')
        data = {}
        for item in items:
            team_elem = item.find('p', 'outright-item__runner-name')
            odd_elem = item.find('button', 'btn-odds')
            team = team_elem.text.strip()
            odd = self.get_odd_value(odd_elem.text.strip())
            data[team] = odd

        self._data = data

    def get_odd_value(self, text):
        if '/' in text:
            nominator, denominator = map(int, text.split('/'))
            return nominator / denominator

        try:
            return float(text)
        except ValueError:
            return text


class PaddyPowerParser(BaseParser):
    def __init__(self, engine_cls=_BSEngine):
        self.engine = engine_cls()

    def parse(self, html):
        self.engine.process(html)
        return self.engine.data
