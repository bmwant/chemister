import timeit
from functools import wraps

import click
import pandas as pd
import numpy as np
from humanfriendly import format_timespan

import settings


DATE_FMT = '%d.%m.%Y'


def load_data(year=2018):
    filename = 'uah_to_usd_{year}.csv'.format(year=year)
    filepath = settings.PROJECT_ROOT / 'notebooks/data' / filename
    df = pd.read_csv(filepath)

    # y = df['sale'].values.reshape(-1, 1)  # targets
    y = df['sale'].values
    X = np.arange(len(y)).reshape(-1, 1)
    return X, y


def load_year_dataframe(year: int=2018, currency: str='usd'):
    filename = 'uah_to_{currency}_{year}.csv'.format(
        year=year,
        currency=currency.lower()
    )
    filepath = settings.PROJECT_ROOT / 'notebooks/data' / filename
    df = pd.read_csv(filepath)
    return df


def hldit(func):
    """
    How Long Doest It Take
    """
    @wraps(func)
    def inner(*args, **kwargs):
        t1 = timeit.default_timer()
        result = func(*args, **kwargs)
        t2 = timeit.default_timer()
        dt = format_timespan(t2-t1)
        click.secho(f'\n{func.__name__} finished in {dt}', fg='cyan')
        return result

    return inner
