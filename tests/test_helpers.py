import pytest

from crawler.helpers import load_config


@pytest.mark.run_loop
async def test_load_config():
    result = await load_config()
    # import pdb; pdb.set_trace()
    print(result)

    # from crawler.db import go
    #
    # r = await go()
    # import pdb; pdb.set_trace()
