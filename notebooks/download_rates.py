import sys
import csv
import concurrent.futures
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import requests


MAX_WORKERS = 20
FILENAME = 'uah_to_usd_2014.csv'

CURRENCIES = (
    'USD',
    'EUR',
    'RUB',
)


def download_url(url):
    r = requests.get(url)
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


def write_data(data):
    header = ['date', 'buy', 'sale', 'buy_nb', 'sale_nb']
    filename_tpl = 'data/uah_to_{currency}_{year}.csv'
    for currency in CURRENCIES:
        filename = filename_tpl.format(currency=currency.lower(), year=2014)
        print('Writing result to a file', filename)
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for item in data:
                row = {'date': item['date'], **item[currency]}
                writer.writerow(row)


def main():
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
                errors.append(url)

    print('\nDone fetching data from API')
    write_data(result)
    print('\nErrors ', len(errors))
    print('\n'.join(errors))


if __name__ == '__main__':
    main()
