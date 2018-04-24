import pytest

from crawler.models.phone import add_new_phone_to_blacklist


@pytest.mark.run_loop
async def test_adding_new_phone_to_blacklist(pg_engine):

    async with pg_engine.acquire() as conn:
        row_id = await add_new_phone_to_blacklist(
            conn,
            phone_number='+380987776655',
            reason='Сказав, що ми дибіли'
        )
        assert isinstance(row_id, int)
