import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score

from notebooks.helpers import load_data


def main():
    year = 2018
    X, y = load_data(year=year)

    days = 31
    # Split the data into training/testing sets
    X_train = X[:-days]
    X_test = X[-days:]

    y_train = y[:-days]
    y_test = y[-days:]

    # Create a bunch of different models
    models = [
        # linear_model.LinearRegression(),
        SVR(kernel='rbf', C=1.0, gamma=0.1),
    ]

    for model in models:
        print('Training model %s' % model)
        model.fit(X_train, y_train)
        # Make predictions using the testing set
        y_pred = model.predict(X_test)
        # Get data for the train set to visualize
        y_learned = model.predict(X_train)
        visualize(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            y_pred=y_pred,
            y_learned=y_learned,
            days=days,
            year=year,
        )

    # # The coefficients
    # print('Coefficients: \n', regr.coef_)
    # # The mean squared error
    # print('Mean squared error: %.2f'
    #       % mean_squared_error(y_test, y_pred))
    # # Explained variance score: 1 is perfect prediction
    # print('Variance score: %.2f' % r2_score(y_test, y_pred))


def visualize(
    *,
    X_train, y_train,
    X_test, y_test,
    y_pred, y_learned,
    days: int, year: int,
):
    # Plot outputs
    plt.figure(figsize=(16, 9))

    # Original for the whole range
    plt.scatter(X_train, y_train,  color='black', s=1)
    plt.scatter(X_test, y_test,  color='magenta', s=1)

    # Predicted for the whole range
    plt.plot(X_test, y_pred, color='cyan', linewidth=2)
    plt.plot(X_train, y_learned, color='blue', linewidth=2)

    plt.xlabel('Day number')
    plt.ylabel('Price')
    plt.legend()
    plt.title('Predictions for %d days for %d' % (days, year))
    plt.show()


if __name__ == '__main__':
    main()
