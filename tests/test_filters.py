import operator
import collections
from crawler.filters import Filter, Container


def test_filter():
    data = [
        {'a': 20, 'b': 5},
        {'a': 10, 'b': 5},
        {'a': 30, 'b': 5},
        {'a': 70, 'b': 5},
    ]

    container = Container(data)
    result = container >> Filter('a', operator.gt, 20)
    assert isinstance(result, collections.Sequence)
    assert len(result) == 2


def test_filters_chain():
    data = [
        {'a': 20, 'b': 7},
        {'a': 10, 'b': 5},
        {'a': 30, 'b': 7},
        {'a': 70, 'b': 5},
        {'a': 50, 'b': 6},
    ]
    container = Container(data)
    result = container >> Filter('a', operator.ne, 20) >> \
        Filter('b', operator.eq, 7)

    assert isinstance(result, collections.Sequence)
    assert len(result) == 1
