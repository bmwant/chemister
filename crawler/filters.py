from collections import UserList


class Container(UserList):
    def __rshift__(self, other):
        if not isinstance(other, Filter):
            raise ValueError('Create correct Filter instance first')

        filtered_data = [
            elem for elem in self.data if self._filter(elem, other)
        ]
        return Container(filtered_data)

    def _filter(self, elem, filter):
        return filter.op(self._get_elem_value(elem, filter.prop), filter.value)

    def _get_elem_value(self, elem, prop):
        if hasattr(elem, prop):
            return getattr(elem, prop)

        if prop in elem:
            return elem[prop]

        raise ValueError('Cannot get %(prop)s from element %(elem)s' %
                         dict(prop=prop, elem=elem))


class Filter(object):
    def __init__(self, prop, op, value):
        self.prop = prop
        self.op = op
        self.value = value
