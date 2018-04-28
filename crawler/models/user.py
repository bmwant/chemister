import sqlalchemy as sa

from . import metadata


user = sa.Table(
    'user', metadata,
    sa.Column('id', sa.Integer, nullable=False),
    sa.Column('name', sa.String, nullable=False),
    sa.Column('email', sa.String, nullable=False),
    sa.Column('password', sa.String, nullable=False),
    sa.Column('permissions', sa.JSON),

    sa.PrimaryKeyConstraint('id', name='user_id_pkey'),
)


async def insert_new_user(conn):
    pass


async def get_user_by_id(conn, user_id):
    query = user.select().where(user.c.id == user_id)

    result = await conn.execute(query)
    return await result.fetchone()


async def get_user(conn, email, password):
    query = user.select().where(sa.and_(
        user.c.email == email,
        user.c.password == password,
    ))

    result = await conn.execute(query)
    return await result.fetchone()
