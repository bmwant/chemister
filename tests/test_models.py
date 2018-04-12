import yaml

from crawler.models import Resource, FetcherConfig, ProxyConfig


SINGLE_DATA = """
- name: The Name 1
  url: "https://example.com/"
  parser: "the_name_parser"
  fetcher:
    instance: "browser"
    driver: "chrome"
  proxy:
    use: true
    ip: "163.172.175.210"
    port: 3128
"""


DEFAULT_DATA = """
- name: The Default 1
  url: "https://example.com/default1"
  proxy:
    use: false
- name: The Default 2
  url: "https://example.com/default2"
  parser: "the_name_parser"
  fetcher:
    instance: "simple"
"""


def test_resource_loading():
    data = yaml.load(SINGLE_DATA)
    result = [Resource(**r) for r in data]
    assert len(result) == 1
    resource = result[0]
    assert isinstance(resource, Resource)
    assert isinstance(resource.proxy, ProxyConfig)
    assert isinstance(resource.fetcher, FetcherConfig)

    assert resource.proxy.use is True
    assert resource.proxy.port == 3128
    assert resource.fetcher.instance == 'browser'
    assert resource.fetcher.driver == 'chrome'


def test_default_values_loaded():
    data = yaml.load(DEFAULT_DATA)
    result = [Resource(**r) for r in data]
    assert len(result) == 2

    res1 = result[0]
    assert res1.fetcher.instance == 'simple'
    assert res1.fetcher.driver is None

    assert res1.proxy.use is False
    assert res1.proxy.ip is None
    assert res1.proxy.port == 80

    res2 = result[1]
    assert res2.fetcher.instance == 'simple'
    assert res2.fetcher.driver is None

    assert res2.proxy.use is False
    assert res2.proxy.ip is None
    assert res2.proxy.port == 80
