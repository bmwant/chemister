import sqlalchemy as sa

from . import metadata


user = sa.Table(
    'resource', metadata,
    sa.Column('id', sa.Integer),
    # sa.Column('name', sa.String),
    # sa.Column('url', sa.String),
    #
    sa.PrimaryKeyConstraint('id', name='user_id_pkey'),
)
