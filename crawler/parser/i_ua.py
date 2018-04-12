import re
import base64
from itertools import takewhile

from bs4 import BeautifulSoup

from utils import LoggableMixin
from crawler.parser import BaseParser, BaseEngine


class _BSEngine(BaseEngine, LoggableMixin):
    def process(self, html):
        soup = BeautifulSoup(html, 'html5lib')
        rows = soup.select('tbody tr')
        data = []
        for row in rows:
            cells = row.find_all('td')
            new_bid = {
                'rate': cells[1].text,
                'amount': cells[2].text,
                'phone': self._extract_phone(cells[3])
            }
            # import pdb; pdb.set_trace()
            data.append(new_bid)
        self._data = data

    def _extract_phone(self, cell):
        link = cell.find('span', 'a')
        handler = link.attrs['onclick']
        pattern = r"showPhone\(this, '(\S+)'\)"
        match_phone = re.match(pattern, handler)
        if match_phone is None:
            self.logger.warning('Cannot match the string %s' % handler)
            return
        encoded_second_part = match_phone.group(1)

        first_part = ''.join(
            takewhile(str.isprintable, cell.text)).replace(' ', '')
        second_part = base64.b64decode(encoded_second_part).decode().strip()

        encoded_phone = first_part + second_part
        return encoded_phone


class IUaParser(BaseParser):
    def __init__(self, engine_cls=_BSEngine):
        self.engine = engine_cls()

    def parse(self, html):
        self.engine.process(html)
        return self.engine.data
