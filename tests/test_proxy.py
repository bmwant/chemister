from http import HTTPStatus

import pytest

from crawler.fetcher.simple import SimpleFetcher
from crawler.proxy import Proxy


@pytest.fixture
def fetcher(loop):
    fetcher = SimpleFetcher(None)
    yield fetcher
    loop.run_until_complete(fetcher.close())


@pytest.mark.run_loop
@pytest.mark.external
async def test_response_without_proxy(fetcher):
    url = 'https://www.skybet.com'
    with pytest.raises(RuntimeError) as e:
        await fetcher.request(url)

    assert str(e.value) == f'Incorrect response: {HTTPStatus.FORBIDDEN}'


@pytest.mark.run_loop
@pytest.mark.external
async def test_response_with_proxy(fetcher):
    proxy = Proxy(ip='138.68.140.197', port=3128)
    fetcher.install_proxy(proxy)
    url = 'https://www.skybet.com'
    resp = await fetcher.request(url)
    assert isinstance(resp, str)
    assert 'Sky Bet' in resp
