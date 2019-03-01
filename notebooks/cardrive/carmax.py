import math
import random
import operator
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm


ENVIRONMENT = [
    (40, 1),
    (35, 1),
    (42, 1),
    (37, 1),
    (34, 1),
    (33, 1),
    (39, 1),
    (44, 1),
    (41, 1),
    (45, 1),
]


ACTIONS = (
    (30, 0),  # buy 30L without driving
    (20, 0),
    (10, 0),
    (0, 0),  # have some rest
    (-10, 10),
    (-20, 20),
    (-30, 30),  # burn 30L of fuel to drive 30 km
)


class EnvData(object):
    def __init__(self, step: int, gas_price: float, consumption: float):
        self.step = step
        self.gas_price = gas_price
        self.consumption = consumption


class BaseAgent(ABC):
    def __init__(self, lip=False):
        self.lip = lip  # verbose

    @abstractmethod
    def take_action(self, *args, **kwargs) -> int:
        pass


class NNBasedDriver(BaseAgent):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

    def take_action(self, *, tank, money, distance, data) -> int:
        input_data = np.array([[
            data.gas_price,
            data.consumption,
            money,
            tank,
            distance,
        ]])
        prediction = self.model.predict(input_data)
        return np.argmax(prediction)


class RandomActionDriver(BaseAgent):
    def take_action(self, *, tank, money, distance, data) -> int:

        # choose random action until it's valid
        while True:
            action_num = random.randrange(len(ACTIONS))
            d_tank, d_distance = ACTIONS[action_num]
            if tank + d_tank >= 0:
                if self.lip:
                    print('\nTime: %d' % data.step)
                    if d_tank > 0:
                        print('>>> Buying %d L of a fuel' % d_tank)
                    elif d_distance:
                        print('>>> Travelling %d km' % d_distance)
                    else:
                        print('>>> Having some rest')

                return action_num


class Car(object):
    def __init__(self, driver: BaseAgent):
        self.tank_history = []
        self.distance_history = []
        self.fund_history = []
        self.driver = driver

    def step(self, data):
        action_num = self.driver.take_action(
            tank=self.tank,
            money=self.money,
            distance=self.distance,
            data=data,
        )

        d_tank, d_distance = ACTIONS[action_num]
        if d_tank > 0:
            money = self.money - data.gas_price*d_tank
        else:
            money = self.money
        tank = self.tank + d_tank
        distance = self.distance + d_distance/data.consumption

        data_row = (
            data.gas_price,
            data.consumption,
            self.money,
            self.tank,
            self.distance,
            action_num,
        )

        self.tank_history.append(tank)
        self.distance_history.append(distance)
        self.fund_history.append(money)

        return data_row

    @property
    def distance(self):
        return self.distance_history[-1] if self.distance_history else 0

    @property
    def tank(self):
        return self.tank_history[-1] if self.tank_history else 0

    @property
    def money(self):
        return self.fund_history[-1] if self.fund_history else 0


def show_history(tank, distance, money):
    # fig, ax = plt.subplots(figsize=(12, 8))
    t = np.arange(0, len(tank))

    fig, axs = plt.subplots(3, 1)
    fig.canvas.set_window_title('RL Driver')
    tank_axs, dist_axs, money_axs = axs
    tank_axs.plot(t, tank)
    tank_axs.set_title('Tank volume')
    tank_axs.set_xlabel('step, t')
    tank_axs.set_ylabel('volume, l')
    tank_axs.xaxis.set_ticks(t)
    tank_axs.grid(True)

    dist_axs.plot(t, distance)
    dist_axs.set_title('Distance travelled')
    dist_axs.set_xlabel('step, t')
    dist_axs.set_ylabel('distance, km')
    dist_axs.xaxis.set_ticks(t)
    dist_axs.grid(True)

    money = list(map(lambda x: -x, money))
    money_axs.plot(t, money)
    money_axs.set_title('Money spent')
    money_axs.set_xlabel('step, t')
    money_axs.set_ylabel('money, $')
    money_axs.xaxis.set_ticks(t)
    money_axs.grid(True)

    fig.tight_layout()
    plt.show()


def play_trip(agent):
    """
    Simulate our trip containing just 10 steps
    """
    car = Car(driver=agent)
    for i, (gas_price, consumption) in enumerate(ENVIRONMENT):
        env_data = EnvData(
            step=i,
            gas_price=gas_price,
            consumption=consumption,
        )
        car.step(env_data)

    print('We have driven %d km' % car.distance)
    print('We have spent %.2f$' % car.money)
    print('Efficiency %.2f' % (car.distance / math.log(-car.money)))
    show_history(
        tank=car.tank_history,
        distance=car.distance_history,
        money=car.fund_history,
    )


def random_play():
    driver = RandomActionDriver(lip=True)
    play_trip(agent=driver)


def nn_play():
    from carmax_nn import create_model
    model = create_model()
    model.load('nn01model.tflearn')
    driver = NNBasedDriver(model=model)
    play_trip(driver)


def collect_data():
    """
    Select top 1K games to train neural network on it later.
    """
    TOP_GAMES = 1000
    NUM_GAMES = 10000
    driver = RandomActionDriver()
    data = []
    for n in tqdm(range(NUM_GAMES)):
        # Reset env
        car = Car(driver=driver)
        game_data = []
        for i, (gas_price, consumption) in enumerate(ENVIRONMENT):
            env_data = EnvData(
                step=i,
                gas_price=gas_price,
                consumption=consumption,
            )
            row = car.step(env_data)
            game_data.append(row)

        coef = car.distance ** 2 / math.log(-car.money)  # ride efficiency
        data.append((coef, game_data))

    # Choose games with best efficiency
    top_data = sorted(data,
                      key=operator.itemgetter(0), reverse=True)[:TOP_GAMES]
    return top_data


def write_data(data):
    df_data = []
    for coef, game_data in data:
        for row in game_data:
            df_data.append(row)

    df = pd.DataFrame(df_data)

    # print(df.head(100))
    df.to_csv('play_data.csv', index=False, header=False)



if __name__ == '__main__':
    # random_play()
    nn_play()
    # data = collect_data()
    # write_data(data)
