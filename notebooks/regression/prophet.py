import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from fbprophet import Prophet
from pandas.plotting import register_matplotlib_converters
from sklearn.metrics import mean_squared_error, r2_score

from notebooks.helpers import load_year_dataframe, DATE_FMT
from notebooks.regression.predict import visualize


register_matplotlib_converters()


def visualize_prophet(
        *,
        data_train, 
        data_test, 
        y_pred,
        y_learned,
        days, 
        year,
):
    train_count = len(data_train.index)
    test_count = len(data_test.index)
    X_train = np.arange(train_count)
    X_test = np.arange(train_count, train_count + test_count)
    y_train = data_train['y']
    y_test = data_test['y']
    y_pred = y_pred['yhat']
    y_learned = y_learned['yhat']

    visualize(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        y_pred=y_pred,
        y_learned=y_learned,
        days=days, year=year,
    )


def main():
    year = 2018
    days = 31  # predict last month
    df = load_year_dataframe(year=year)
    df['ds'] = pd.to_datetime(df['date'], format=DATE_FMT)
    df['y'] = df['sale']
    data = df[['ds', 'y']].copy()

    data_train = data[:-days]
    data_test = data[-days:]
    print('Training model...')
    model = Prophet()
    model.fit(data_train)

    print('Predicting...')
    y_pred = model.predict(data_test)
    print(y_pred[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
    y_learned = model.predict(data_train)
    print('Mean squared error: %.2f' % 
          mean_squared_error(data_test['y'], y_pred['yhat']))
    print('Variance score: %.2f' % r2_score(data_test['y'], y_pred['yhat']))

    fig1 = model.plot(y_pred)
    fig2 = model.plot_components(y_pred)
    plt.show()
    # visualize_prophet(
    #     data_train=data_train, 
    #     data_test=data_test,
    #     y_pred=y_pred,
    #     y_learned=y_learned,
    #     days=days, 
    #     year=year,
    # )


if __name__ == '__main__':
    main()

