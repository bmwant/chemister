from bs4 import BeautifulSoup

from crawler.parser import BaseParser, BaseEngine


class _RegexEngine(BaseEngine):
    def process(self, html):
        html = html.replace('<!---->', '')
        soup = BeautifulSoup(html, 'html5lib')
        team_elem = 'ui-scoreboard-runner'
        team_class = 'ui-scoreboard-runner__home'
        teams = [e.getText().strip()
                 for e in soup.find_all(team_elem, team_class)]

        get_odds_elems = lambda x: x.find('btn-odds',
                                          class_='avb-item__btn-odds')
        get_odds_text = lambda x: x.getText().strip()
        odds_elems = map(get_odds_elems, soup.find_all('avb-item'))
        odds = map(get_odds_text, odds_elems)
        odds_values = map(self.get_odd_value, odds)
        self._data = dict(zip(teams, odds_values))

    def get_odd_value(self, text):
        if text == 'EVS':
            return text

        if '/' in text:
            nominator, denominator = map(int, text.split('/'))
            return nominator / denominator

        try:
            return float(text)
        except ValueError:
            return text


class WilliamHillParser(BaseParser):
    def __init__(self, engine_cls=_RegexEngine):
        self.engine = engine_cls()

    def parse(self, html):
        self.engine.process(html)
        return self.engine.data


"""
tree sketch
"""
