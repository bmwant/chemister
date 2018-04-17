from aiopg.sa import create_engine
from sqlalchemy.dialects import postgresql

import settings


async def get_engine():
    engine = await create_engine(
        settings.DATABASE_DSN,
        minsize=settings.DATABASE_POOL_MINSIZE,
        maxsize=settings.DATABASE_POOL_MAXSIZE,
    )
    return engine


def show_sql_query_for_clause(sa_clause, logger=None):
    # todo: this does not display values
    # http://docs.sqlalchemy.org/en/latest/faq/sqlexpressions.html#faq-sql-expression-string
    compiled_query = sa_clause.compile(dialect=postgresql.dialect())
    sql_query = compiled_query.string
    if logger is not None:
        logger.debug(sql_query)
    return sql_query
