from crawler.parser.paddy_power import PaddyPowerParser
from crawler.parser.sky_bet import SkyBetParser
from crawler.parser.william_hill import WilliamHillParser


TEAMS_NUMBER = 32


def test_paddy_power_parser(page_html):
    html = page_html('paddy_power')
    parser = PaddyPowerParser()
    data = parser.parse(html=html)

    assert 'England' in data
    assert 'Portugal' in data
    assert 'Uruguay' in data

    assert all([isinstance(k, str) for k in data.keys()])
    assert all([isinstance(v, float) for v in data.values()])

    assert len(data) == TEAMS_NUMBER


def test_sky_bet_parser(page_html):
    html = page_html('sky_bet')
    parser = SkyBetParser()
    data = parser.parse(html=html)

    assert 'Brazil' in data
    assert 'Poland' in data
    assert 'Russia' in data

    assert all([isinstance(k, str) for k in data.keys()])
    assert all([isinstance(v, float) for v in data.values()])

    assert len(data) == TEAMS_NUMBER


def test_william_hill_parser():
    parser = WilliamHillParser()
    data = parser.parse(html='')
