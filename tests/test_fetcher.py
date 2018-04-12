import pytest

from crawler.proxy import Proxy
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


@pytest.mark.run_loop
@pytest.mark.external
async def test_browser_fetcher(browser_fetcher):
    url = ('https://www.paddypower.com/'
           'football/2018-fifa-world-cup?tab=outrights')
    resp = await browser_fetcher.request(url)

    assert 'Brazil' in resp
    # Check hidden element is on page too
    assert 'South Korea' in resp
    assert 'Costa Rica' in resp


@pytest.mark.run_loop
@pytest.mark.external
async def test_browser_fetcher_with_proxy_reveals_hidden_elements(
    browser_fetcher_with_proxy
):
    url = 'https://m.skybet.com/football/world-cup-2018/event/16742642'
    resp = await browser_fetcher_with_proxy.request(url)

    assert 'Australia</div>' in resp
    assert 'Tunisia</div>' in resp
    assert 'Panama</div>' in resp
    assert 'Mexico</div>' in resp
    assert 'Costa Rica</div>' in resp
    assert 'Korea Republic</div>' in resp
    assert 'Switzerland</div>' in resp
    # Element was clicked and not on the page anymore
    assert 'Show All' not in resp
