from crawler.parser.i_ua import IUaParser


def test_i_ua_parser(page_html):
    html = page_html('i_ua')
    parser = IUaParser()
    data = parser.parse(html=html)
