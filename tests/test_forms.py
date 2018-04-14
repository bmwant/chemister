from crawler.forms.config import config_trafaret


def test_config_loading():
    FORM_DATA = {
        'MIN_BID_AMOUNT': '100',
        'MAX_BID_AMOUNT': '2000',
        'DRY_RUN': 'on',
        'CLOSED_BIDS_FACTOR': '1',
        'TIME_DAY_ENDS': '20:00',
        'REFRESH_PERIOD_MINUTES': '5',
    }
    result = config_trafaret.check(FORM_DATA)
    assert isinstance(result, dict)
    assert isinstance(result['MIN_BID_AMOUNT'], float)
