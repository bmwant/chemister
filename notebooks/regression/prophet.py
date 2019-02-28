import pandas as pd
from fbprophet import Prophet

from notebooks.helpers import load_year_dataframe, DATE_FMT


def main():
    df = load_year_dataframe(year=2018)
    df['ds'] = pd.to_datetime(df['date'], format=DATE_FMT)
    df['y'] = df['sale']
    data = df[['ds', 'y']].copy()

    days = 31  # predict last month
    data_train = data[:-days]
    data_test = data[-days:]
    print('Training model...')
    model = Prophet()
    model.fit(data_train)

    print('Predicting...')
    forecast = model.predict(data_test)
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())


if __name__ == '__main__':
    main()

