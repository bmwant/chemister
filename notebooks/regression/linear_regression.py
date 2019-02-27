import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

from notebooks.helpers import load_data


def main():
    year = 2018
    X, y = load_data(year=year)

    days = 20
    # Split the data into training/testing sets
    X_train = X[:-days]
    X_test = X[-days:]

    y_train = y[:-days]
    y_test = y[-days:]

    # Create linear regression object
    regr = linear_model.LinearRegression()

    # Train the model using the training sets
    regr.fit(X_train, y_train)

    # Make predictions using the testing set
    y_pred = regr.predict(X_test)

    # The coefficients
    print('Coefficients: \n', regr.coef_)
    # The mean squared error
    print('Mean squared error: %.2f'
          % mean_squared_error(y_test, y_pred))
    # Explained variance score: 1 is perfect prediction
    print('Variance score: %.2f' % r2_score(y_test, y_pred))

    # Plot outputs
    plt.figure(figsize=(16, 9))
    
    plt.scatter(X_train, y_train,  color='black', s=1)
    plt.scatter(X_test, y_test,  color='magenta', s=1)
    plt.plot(X_test, y_pred, color='cyan', linewidth=2)
    plt.plot(X_train, regr.predict(X_train), color='blue', linewidth=2)

    plt.xlabel('Day number')
    plt.ylabel('Price')
    plt.legend()
    plt.title('Predictions for %d days for %d' % (days, year))
    plt.show()


if __name__ == '__main__':
    main()
