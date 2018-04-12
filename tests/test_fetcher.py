import pytest

from crawler.proxy import Proxy
from crawler.fetcher.simple import SimpleFetcher
from crawler.fetcher.browser import BrowserFetcher


@pytest.fixture
def browser_fetcher(loop):
    fetcher = BrowserFetcher(None)
    yield fetcher
    loop.run_until_complete(fetcher.close())


@pytest.fixture
def browser_fetcher_with_proxy(loop):
    proxy = Proxy(ip='163.172.175.210', port=3128)
    fetcher = BrowserFetcher(None, proxy=proxy)
    yield fetcher
    loop.run_until_complete(fetcher.close())


@pytest.fixture
def simple_fetcher(loop):
    fetcher = SimpleFetcher(None)
    yield fetcher
    loop.run_until_complete(fetcher.close())


@pytest.mark.run_loop
@pytest.mark.external
async def test_fetch_i_ua(simple_fetcher):
    url = 'https://finance.i.ua/market/kiev/usd/?type=1'
    resp = await simple_fetcher.request(url)

    # with open('f.html', 'w') as f:
    #     f.write(resp)
