from html.parser import HTMLParser

from crawler.parser import BaseParser, BaseEngine


class _HTMLParserEngine(HTMLParser, BaseEngine):
    def __init__(self):
        super().__init__()
        BaseEngine.__init__(self)

        self._team_class = None
        self._odd_class = None
        self._team_found = False
        self._odd_found = False

        self._team_tmp = None
        self._odd_tmp = None

    def process(self, html):
        self.feed(html)

    def _get_team_class(self):
        """
        Implementation is easy to change in case classes will be generated
        dynamically.
        """
        return '_e4y4wr'

    def _get_odd_class(self):
        """
        Implementation is easy to change in case classes will be generated
        dynamically.
        """
        return '_1jca28'

    @property
    def odd_class(self):
        if self._odd_class is None:
            self._odd_class = self._get_odd_class()

        return self._odd_class

    @property
    def team_class(self):
        if self._team_class is None:
            self._team_class = self._get_team_class()

        return self._team_class

    def _get_tag_class(self, tag_attrs):
        for name, value in tag_attrs:
            if name == 'class':
                return value

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and self._get_tag_class(attrs) == self.team_class:
            self._team_found = True
            return

        if tag == 'span' and self._get_tag_class(attrs) == self.odd_class:
            self._odd_found = True
            return

    def handle_data(self, data):
        if self._team_found:
            self._team_tmp = data
            self._team_found = False

        if self._odd_found:
            self._odd_tmp = data
            self._odd_found = False

        if self._team_tmp and self._odd_tmp:
            team = self._team_tmp.strip()
            odd = self.get_odd_value(self._odd_tmp)
            self._data[team] = odd
            self._team_tmp = None
            self._odd_tmp = None

    def get_odd_value(self, text):
        nominator, denominator = map(int, text.split('/'))
        return nominator / denominator


class SkyBetParser(BaseParser):
    def __init__(self, engine_cls=_HTMLParserEngine):
        self.engine = engine_cls()

    def parse(self, html):
        self.engine.process(html)
        result = self.engine.data
        return result
