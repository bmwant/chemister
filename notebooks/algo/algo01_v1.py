from datetime import datetime, timedelta

import pandas as pd

from download_rates import DATE_FMT


def main():
    year = 2017
    currency = 'usd'
    filename = 'data/uah_to_{}_{}.csv'.format(currency, year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT) 
    sd = datetime.strptime('01.01.{}'.format(year), DATE_FMT) 
    ed = datetime.strptime('31.12.{}'.format(year), DATE_FMT)

    amount_daily = 100  # how many to buy daily
    shift = 10  # delay in days between buying and selling
    total_uah = 10000  # initial value of money we have
    total_usd = 0

    i = 0
    transactions = 0
    skipped = 0
    current_date = sd  # starting date
    while current_date <= ed:  # until end date
        rate_sale = df.loc[df['date'] == current_date.strftime(DATE_FMT)]['sale'].item()
        # sale first to use money when buying currency
        date_sale = current_date - timedelta(days=shift)
        if date_sale >= sd:
            rate_buy = df.loc[df['date'] == date_sale.strftime(DATE_FMT)]['buy'].item()
            sale_amount = amount_daily * rate_buy
            if total_usd >= amount_daily:
                total_uah += sale_amount
                total_usd -= amount_daily
                transactions += 1
            else:
                print('...skipping SALE, not enough money')
                skipped += 1

        # buy specified amount
        buy_amount = amount_daily * rate_sale
        if total_uah >= buy_amount:
            total_uah -= amount_daily * rate_sale
            total_usd += amount_daily
            print('{} | rate: {:.2f} | buy: {:.2f} | UAH: {:.2f}, USD: {:.2f}'.format(
                current_date.strftime(DATE_FMT), rate_sale, amount_daily*rate_sale, total_uah, total_usd,
            ))
            transactions += 1
        else:
            print('...skipping BUY, not enough money')
            skipped += 1

        i += 1
        current_date += timedelta(days=1)

    # close period to calculate raw profit in uah
    close_buy_rate = df.loc[df['date'] == ed.strftime(DATE_FMT)]['buy'].item()
    close_uah  = total_uah + close_buy_rate*total_usd
    print('Close amount: {:.2f} UAH'.format(close_uah))
    print('Total iterations: {}'.format(i))
    print('Total transactions: {}'.format(transactions))
    print('Transaction skipped: {}'.format(skipped))
    print('We have {:.2f} UAH'.format(total_uah))
    print('We have {:.2f} USD in total'.format(total_usd))
    

if __name__ == '__main__':
    main()
