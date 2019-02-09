import sys
import csv
import time
import timeit
import random
import argparse
import concurrent.futures
from functools import wraps
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import requests


MAX_RETRIES = 20
MAX_WORKERS = 4
MIN_SLEEP = 10
MAX_SLEEP = 60

HEADER = ['date', 'buy', 'sale', 'nb']
DATE_FMT = '%d.%m.%Y'
CURRENCIES = (
    'USD',
    'EUR',
    'RUB',
)


class Downloader(object):
    def __init__(self, urls, *, max_workers=MAX_WORKERS):
        self.urls = urls
        self._missing = []
        self._errors = []
        self._max_workers = max_workers

    def download(self):
        results = []
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            future_to_url = {
                executor.submit(download_url, url): url
                for url in self.urls
            }
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results.append(self.process_item(future.result()))
                    sys.stdout.write(
                        '\r{}/{} requests completed...'.format(len(results), len(self.urls)))
                    sys.stdout.flush()
                except Exception as e:
                    self._errors.append('{}: {}'.format(url, e))

        return results

    def process_item(self, item):
        date = item['date']
        result = {
            'date': date
        }
        rates = item['exchangeRate']
        for item in rates:
            currency = item.get('currency')  # currency key might be missing in data
            if currency not in CURRENCIES:
                continue
            # Required, throw KeyError if not present
            result[currency] = {
                'nb': item['saleRateNB'],
                'buy': item['purchaseRate'],
                'sale': item['saleRate'],
            }

        # Check missing data
        for currency in CURRENCIES:
            if currency not in result:
                self._missing.append('Missing {} for {}'.format(currency, date))
        return result

    def info(self):
        print('\nDone fetching data for {} urls'.format(len(self.urls)))
        print('\nMissing data', len(self._missing))
        print('\n'.join(self._missing))
        print('\nErrors', len(self._errors))
        print('\n'.join(self._errors))


class RetryError(RuntimeError):
    pass


def retry(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        for r in range(MAX_RETRIES+1):
            try:
                return fn(*args, **kwargs)
            except RetryError:
                delay = random.randint(MIN_SLEEP, MAX_SLEEP)
                time.sleep(delay)
        raise RuntimeError(
            'Cannot successfully execute {} with {} retries'.format(fn.__name__, r)
        )

    return wrapper


@retry
def download_url(url):
    r = requests.get(url)
    if r.status_code == requests.codes.too_many:
        raise RetryError()

    if r.status_code != requests.codes.ok:
        raise RuntimeError('{}: {}'.format(r.status_code, r.text))
    return r.json()


def append_rows(*, filename, rows, fieldnames):
    with open(filename, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for row in rows:
            writer.writerow(row)


def write_data(data, year, append=False):
    filename_tpl = 'data/uah_to_{currency}_{year}.csv'
    for currency in CURRENCIES:
        filename = filename_tpl.format(currency=currency.lower(), year=year)
        print('\nWriting result to a file', filename)
        if not append:
            with open(filename, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=HEADER)
                writer.writeheader()
        rows = [{'date': item['date'], **item[currency]} for item in data]
        append_rows(
            filename=filename,
            rows=rows,
            fieldnames=HEADER,
        )


def generate_urls(start_date, end_date):
    url_template = 'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
    urls = []
    date_iter = start_date
    while date_iter <= end_date:
        url = url_template.format(date=date_iter.strftime(DATE_FMT))
        urls.append(url)
        date_iter += timedelta(days=1)
    return urls


def main(year, start_day, start_month, end_day, end_month):
    start_date_str = '{:02d}.{:02d}.{}'.format(start_day, start_month, year)
    end_date_str = '{:02d}.{:02d}.{}'.format(end_day, end_month, year)

    print('Range of dates selected [{} - {}]'.format(start_date_str, end_date_str))
    start_date = datetime.strptime(start_date_str, DATE_FMT)
    end_date = datetime.strptime(end_date_str, DATE_FMT)

    urls = generate_urls(start_date, end_date)
    d = Downloader(urls)
    results = d.download()
    write_data(results, year=year)
    d.info()


def main_wrapper():
    parser = argparse.ArgumentParser(description='Download currency data.')
    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='year you want to fetch data for'
    )
    parser.add_argument(
        '--month-start',
        default=1,
        required=False,
        type=int,
        help='month number for the starting date',
    )
    parser.add_argument(
        '--day-start',
        default=1,
        required=False,
        type=int,
        help='day of month for the starting date',
    )
    parser.add_argument(
        '--month-end',
        default=12,
        required=False,
        type=int,
        help='month number for the end date',
    )
    parser.add_argument(
        '--day-end',
        default=31,
        required=False,
        type=int,
        help='day of month for the end date',
    )
    args = parser.parse_args()

    t1 = timeit.default_timer()
    main(
        year=args.year,
        start_day=args.day_start,
        start_month=args.month_start,
        end_day=args.day_end,
        end_month=args.month_end,
    )
    t2 = timeit.default_timer()
    print('\nFinished in {:.2f} minutes'.format((t2-t1) / 60.))


if __name__ == '__main__':
    """
    2014 - Finished in 5.02 minutes
    2015 - Finished in 60.70 minutes
    2016 - Finished in 60.87 minutes
    2017 - Finished in 60.71 minutes
    2018 - Finished in 60.70 minutes
    2019 - 
    """
    main_wrapper()
