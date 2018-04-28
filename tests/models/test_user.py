import pytest

from crawler.models.user import get_user_by_id


@pytest.mark.run_loop
async def test_default_admin_user_is_present(pg_engine):

    async with pg_engine.acquire() as conn:
        user = await get_user_by_id(conn, 1)
        assert user.name == 'admin'
        # todo: encrypt password
        assert user.email == 'admin@gmail.com'
        assert user.password == 'admin'
