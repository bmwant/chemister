import sqlalchemy as sa


metadata = sa.MetaData()


async def check_result(result, fetchone=False):
    if result.returns_rows:
        if fetchone:
            return await result.fetchone()
        return await result.fetchall()
