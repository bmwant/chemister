from enum import Enum
from datetime import datetime

import sqlalchemy as sa

from utils import get_logger
from . import metadata


logger = get_logger(__name__)


class EventType(Enum):
    DEFAULT = 'default'
    NOTIFIED = 'notified'
    CALLED = 'called'


event = sa.Table(
    'event', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('description', sa.String, nullable=False),
    sa.Column('event_type', sa.String, nullable=False),
    sa.Column('event_count', sa.Integer, nullable=False, default=1),
    sa.Column('created', sa.DateTime, nullable=False, default=datetime.now),

    # 0 corresponds to system user, no foreign key constraint
    sa.Column('user_id', sa.Integer, default=0),

    sa.PrimaryKeyConstraint('id', name='event_id_pkey'),
)


async def add_event(
    conn,
    *,
    event_type: EventType=EventType.DEFAULT,
    description: str='',
    event_count: int=1,
    user_id: int=0,  # system
):
    query = event.insert().values(
        event_type=event_type.value,
        description=description,
        event_count=event_count,
        user_id=user_id,
    )
    result = await conn.execute(query)
    row_id = (await result.fetchone())[0]
    return row_id


async def get_events(conn):
    query = event.select()
    result = await conn.execute(query)
    return await result.fetchall()
