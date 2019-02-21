from abc import ABC, abstractmethod
from util import LoggableMixin


class BaseTrader(ABC, LoggableMixin):
    @abstractmethod
    def trade(self, daily_data):
        pass

    def add_transaction(self):
        pass


