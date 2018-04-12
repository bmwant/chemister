

class BaseDriver(object):
    EXECUTABLE_PATH = None
    BINARY_PATH = None

    def __init__(self):
        self._driver = None

    @property
    def driver(self):
        return self._driver
