import pytest

from crawler.cache import Cache


@pytest.fixture
def cache(loop):
    cache = Cache()
    loop.run_until_complete(cache._create_pool())
    yield cache
    loop.run_until_complete(cache.close())


@pytest.mark.run_loop
@pytest.mark.external
async def test_json_data(cache):
    data = {
        'team1': 1,
        'team2': 2,
    }

    await cache.set('test', data)
    result = await cache.get('test')
    assert isinstance(result, dict)
    await cache.close()

