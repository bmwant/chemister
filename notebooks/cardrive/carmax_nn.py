"""
pyenv virtualenv 3.5.6 cardrive
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.1.0-py3-none-any.whl
pip install $TF_BINARY_URL
pip install tflearn
"""
import pandas as pd


def get_data():
    pass


def main():
    X, y = get_data()
    tflearn.init_graph(num_cores=8)

    net = tflearn.input_data(shape=[None, 5])
    net = tflearn.fully_connected(net, 6)
    # net = tflearn.dropout(net, 0.5)
    net = tflearn.fully_connected(net, 7, activation='softmax')
    net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')

    model = tflearn.DNN(net)
    model.fit(X, y)

    # model.predict([])
