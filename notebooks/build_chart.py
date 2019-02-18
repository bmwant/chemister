import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters


def build_chart(df, currency, title='', show_profit=False):
    dates = df['date']
    l_days = mdates.DayLocator()
    l_years = mdates.YearLocator()
    l_months = mdates.MonthLocator()
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.canvas.set_window_title('Exchange rate chart')
    plt.plot(dates, df['buy'], 'b', label='Buy')
    plt.plot(dates, df['sale'], 'm', label='Sale')

    ax.legend()
    # Format the ticks ax
    formatter = mdates.DateFormatter('%d/%m')
    ax.xaxis.set_major_locator(l_months)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_minor_locator(l_days)

    ax.set_xlim(dates.iloc[0], dates.iloc[-1])

    def rate(x):
        return '%.2f' % x

    if show_profit:
        ax.fill_between(dates, df['buy'], df['sale'], where=df['buy'] >= df['sale'], facecolor='c', interpolate=True)
        ax.fill_between(dates, df['buy'], df['sale'], where=df['buy'] < df['sale'], facecolor='y', interpolate=True)

    ax.format_xdata = mdates.DateFormatter('%d/%m/%y')
    ax.format_ydata = rate
    ax.grid(True)

    fig.autofmt_xdate()
    plt.title(title)
    plt.show()


def parse_args():
    pass


def main():
    register_matplotlib_converters()
    year = 2015
    currency = 'rub'
    filename = 'data/uah_to_{}_{}.csv'.format(currency, year)
    df = pd.read_csv(filename)
    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')
    title = 'Buy/sale rates for {}'.format(currency)
    build_chart(df, currency=currency, title=title)


if __name__ == '__main__':
    main()
