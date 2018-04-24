import sqlalchemy as sa

from utils import get_logger
from . import metadata


logger = get_logger(__name__)


phone = sa.Table(
    'phone', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('phone', sa.String, nullable=False),
    sa.Column('reason', sa.String, nullable=False),
    sa.PrimaryKeyConstraint('id', name='phone_id_pkey'),
)


async def add_new_phone_to_blacklist(conn, *, phone_number, reason=''):
    query = phone.insert().values(
        phone=phone_number,
        reason=reason,
    )
    result = await conn.execute(query)
    row_id = (await result.fetchone())[0]
    return row_id

