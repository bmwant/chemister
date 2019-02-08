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

CURRENCIES = (
    'USD',
    'EUR',
    'RUB',
)


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
        import pdb; pdb.set_trace()
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


def process_day(data):
    result = {
        'date': data['date']
    }
    rates = data['exchangeRate']
    for item in rates:
        currency = item['currency']
        if currency not in CURRENCIES:
            continue
        result[currency] = {
            'buy_nb': item['purchaseRateNB'],
            'sale_nb': item['saleRateNB'],
            'buy': item['purchaseRate'],
            'sale': item['saleRate'],
        }

    return result


def write_data(data, year):
    header = ['date', 'buy', 'sale', 'buy_nb', 'sale_nb']
    filename_tpl = 'data/uah_to_{currency}_{year}.csv'
    for currency in CURRENCIES:
        filename = filename_tpl.format(currency=currency.lower(), year=year)
        print('Writing result to a file', filename)
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for item in data:
                row = {'date': item['date'], **item[currency]}
                writer.writerow(row)


def main(year):
    url_template = 'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'
    start_date = datetime.strptime('01.12.2014', '%d.%m.%Y')
    end_date = datetime.strptime('31.12.2014', '%d.%m.%Y')
    # end_date = datetime.now()
    urls = []
    errors = []
    current_date = start_date
    while current_date <= end_date:
        url = url_template.format(date=current_date.strftime('%d.%m.%Y'))
        urls.append(url)
        current_date += timedelta(days=1)

    result = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {
            executor.submit(download_url, url): url
            for url in urls
        }
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                result.append(process_day(data))
                sys.stdout.write('\r{}/{} requests completed...'.format(len(result), len(urls)))
                sys.stdout.flush()
            except Exception as e:
                errors.append('{}: {}'.format(url, e))

    print('\nDone fetching data from API')
    write_data(result, year=year)
    print('\nErrors ', len(errors))
    print('\n'.join(errors))


def main_wrapper():
    parser = argparse.ArgumentParser(description='Download currency data.')
    parser.add_argument(
        '--year',
        required=True,
        type=int,
        help='year you want to fetch data for'
    )
    args = parser.parse_args()

    t1 = timeit.default_timer()
    main(args.year)
    t2 = timeit.default_timer()
    print('\nFinished in {:.2f} minutes'.format((t2-t1) / 60.))


if __name__ == '__main__':
    main_wrapper()
