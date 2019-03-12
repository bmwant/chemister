import pandas as pd

from notebooks.helpers import load_year_dataframe, DATE_FMT 


class EnvData(object):
    def __init__(self, step: int, rate_buy: float, rate_sale: float):
        self.step = step
        self.rate_buy = rate_buy
        self.rate_sale = rate_sale

    def __str__(self):
        return f'{self.step}: {self.rate_buy}/{self.rate_sale}'


class Environment(object):
    def __init__(self):
        self._df = None
        self.step = 0

    def load(self, year: int):
        self._df = load_year_dataframe(year)
        # just make sure rows are ordered by date
        self._df['date'] = pd.to_datetime(self._df['date'], format=DATE_FMT)

        self._df.sort_values(by=['date'], inplace=True)
        self._df.reset_index(drop=True, inplace=True)

    def get_observation(self):
        row = self._df.iloc[[self.step]]
        return EnvData(
            step=self.step,
            rate_buy=float(row['buy']),
            rate_sale=float(row['sale']),
        )


def check():
    e = Environment()
    e.load(year=2017)
    print(e.get_observation())


if __name__ == '__main__':
    check()