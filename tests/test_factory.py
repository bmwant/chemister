from crawler.factory import Factory


def test_resources_loading():
    f = Factory()
    r = f.load_resources()
