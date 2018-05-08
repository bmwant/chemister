import pytest

from crawler.models.user import get_user_by_id
from webapp.helpers import create_password


@pytest.mark.run_loop
async def test_default_admin_user_is_present(pg_engine):
    password = create_password('admin')
    async with pg_engine.acquire() as conn:
        user = await get_user_by_id(conn, 1)
        assert user.name == 'admin'
        assert user.email == 'admin@gmail.com'
        assert user.password == password
