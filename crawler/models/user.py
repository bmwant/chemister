import sqlalchemy as sa

from . import metadata


user = sa.Table(
    'user', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('password', sa.String, nullable=False),
    sa.Column('permissions', sa.JSON),

    sa.PrimaryKeyConstraint('id', name='user_id_pkey'),
)


async def insert_new_user(conn):
    pass
