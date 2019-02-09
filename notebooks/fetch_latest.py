from datetime import datetime

import pandas as pd

from download_rates import generate_urls, Downloader


def main():
    current_date = datetime.now()
    current_year = current_date.year
    # filename = 'data/uah_to_usd_{}.csv'.format(current_year)
    # df = pd.read_csv(filename)
    # df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
    # assuming file has been previously sorted
    # last_row = df.iloc[-1]

    # urls = generate_urls(last_row['date'], current_date)
    sd = datetime.strptime('07.02.2019', '%d.%m.%Y')
    urls = generate_urls(sd, current_date)
    d = Downloader(urls)
    r = d.download()
    d.info()
    print(r)


if __name__ == '__main__':
    main()
