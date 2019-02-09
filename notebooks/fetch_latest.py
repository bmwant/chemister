from datetime import datetime, timedelta

import pandas as pd

from download_rates import generate_urls, write_data, Downloader, DATE_FMT


def main():
    current_date = datetime.now() - timedelta(days=1)
    current_year = current_date.year
    filename = 'data/uah_to_usd_{}.csv'.format(current_year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
    # assuming file has been previously sorted
    last_row = df.iloc[-1]

    start_date = last_row['date'] + timedelta(days=1)
    urls = generate_urls(start_date, current_date)
    print('Range of dates selected [{} - {}]'.format(
        start_date.strftime(DATE_FMT), current_date.strftime(DATE_FMT)))
    if not urls:
        print('Date is already up to date')
        return
    d = Downloader(urls)
    new_results = d.download()
    d.info()
    write_data(new_results, current_year, append=True)


if __name__ == '__main__':
    main()
