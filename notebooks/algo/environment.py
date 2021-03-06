import pandas as pd

from notebooks.helpers import load_year_dataframe, DATE_FMT


class EnvData(object):
    def __init__(self, step: int, rate_buy: float, rate_sale: float):
        self.step = step
        self.rate_buy = rate_buy
        self.rate_sale = rate_sale

    def __str__(self):
        return f'{self.step}: {self.rate_buy:.2f}/{self.rate_sale:.2f}'


class Environment(object):
    def __init__(self):
        self._df = None
        self.step = 0

    def load(self, year: int):
        print(f'Loading environment for {year} year')
        self._df = load_year_dataframe(year)
        # just make sure rows are ordered by date
        self._df['date'] = pd.to_datetime(self._df['date'], format=DATE_FMT)

        self._df.sort_values(by=['date'], inplace=True)
        self._df.reset_index(drop=True, inplace=True)
        # days = 31
        # print(f'Simplify and run just for {days} days')
        # self._df = self._df.head(days)

    def load_demo(self):
        data = [
            (27.9, 28.3),  # buy
            (28.1, 28.3),  # buy
            (28.4, 28.65), # sale
            (28.5, 28.7),  # sale
        ]
        self._df = pd.DataFrame(data, columns=['buy', 'sale'])


    def get_observation(self, step=None):
        step = step or self.step
        row = self._df.iloc[[step]]
        return EnvData(
            step=step,
            rate_buy=float(row['buy']),
            rate_sale=float(row['sale']),
        )

    @property
    def size(self) -> int:
        return len(self._df.index)


def check():
    e = Environment()
    e.load(year=2017)
    print(e.get_observation())
    print(e.size)


if __name__ == '__main__':
    check()
