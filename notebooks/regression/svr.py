import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVR


from notebooks.helpers import load_data


def main():
    year = 2018
    X, y = load_data(year=year)
    svr_lin = SVR(kernel='linear', gamma='scale', C=1.0, epsilon=0.2)
    svr_poly = SVR(kernel='poly', C=1e2, degree=2, gamma='scale')
    svr_rbf = SVR(kernel='rbf', C=1.0, gamma=0.1)
    print('Training linear model...')
    svr_lin.fit(X, y)
    print('Training polynomial model...')
    svr_poly.fit(X, y)
    print('Training RBF model...')
    svr_rbf.fit(X, y)

    print('Plotting data...')
    fig = plt.figure(figsize=(16, 9))
    plt.scatter(X, y, s=1, color='black', label='Rate')
    plt.plot(X, svr_lin.predict(X), color='red', label='Linear model')
    plt.plot(X, svr_poly.predict(X), color='green', label='Polynomial model')
    plt.plot(X, svr_rbf.predict(X), color='blue', label='RBF model')

    plt.xlabel('Day number')
    plt.ylabel('Price')
    plt.legend()
    plt.title('Rate for %d' % year)
    plt.show()


if __name__ == '__main__':
    main()
