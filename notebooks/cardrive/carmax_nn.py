"""
pyenv virtualenv 3.5.6 cardrive
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.1.0-py3-none-any.whl
pip install $TF_BINARY_URL
pip install tflearn
"""
import tflearn
import tensorflow as tf
import numpy as np
import pandas as pd


def get_data():
    num_actions = 7
    df = pd.read_csv('play_data.csv', header=None)
    X = df.loc[:,0:4].to_numpy()  # select first 5 rows
    actions = df.iloc[:,-1]  # select last row
    # convert actions to softmax format
    y = np.zeros((len(actions), num_actions))
    y[np.arange(len(actions)), actions] = 1
    return X, y


def create_model():
    net = tflearn.input_data(shape=[None, 5])
    net = tflearn.fully_connected(net, 6)
    # net = tflearn.dropout(net, 0.5)
    net = tflearn.fully_connected(net, 7, activation='softmax')
    net = tflearn.regression(
        net,
        optimizer='adam',
        loss='categorical_crossentropy',
    )
    model = tflearn.DNN(net)
    return model


def main():
    """
    Supervised learning. Use best results from random agent.
    """
    X, y = get_data()
    # X = np.array([
    #     [1, 2, 3, 4, 5],
    #     [2, 4, 6, 8, 10],
    #     [3, 6, 9, 12, 18],
    #     [4, 8, 12, 16, 20],
    # ])
    #
    # y = np.array([
    #     [1, 0, 0, 0, 0, 0, 1],
    #     [4, 0, 0, 0, 0, 0, 1],
    #     [9, 0, 0, 0, 0, 0, 1],
    #     [16, 0, 0, 0, 0, 0, 1],
    # ])
    # tf.reset_default_graph()
    tflearn.init_graph(num_cores=8)
    print('Creating a model...')
    model = create_model()
    print('Training model based on NN...')
    model.fit(X, y, n_epoch=20)

    print(model.predict([
        [5, 10, 14, 19, 26],
        [1, 2, 3, 4, 5],
        [6, 12, 18, 24, 30],

    ]))
    print('Serializing model to a file...')
    model.save('nn01model.tflearn')
    print('Done')


if __name__ == '__main__':
    main()
