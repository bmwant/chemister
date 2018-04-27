import pytest

from crawler.models.resource import get_resource_by_name


@pytest.mark.run_loop
async def test_get_resource_by_name(pg_engine):
    async with pg_engine.acquire() as conn:
        result = await get_resource_by_name(conn, 'noname')
        assert result is None
