import random
from abc import ABC, abstractmethod

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


class EnvData(object):
    def __init__(self, step: int, gas_price: float, consumption: float):
        self.step = step
        self.gas_price = gas_price
        self.consumption = consumption


class BaseAgent(ABC):
    def __init__(self, lip=False):
        self.lip = lip  # verbose

    @abstractmethod
    def take_action(self, *args, **kwargs):
        pass


class RandomActionDriver(BaseAgent):
    def take_action(self, *, tank, money, distance, data):
        actions = (
            (30, 0),
            (20, 0),
            (10, 0),
            (0, 0),
            (-10, 10),
            (-20, 20),
            (-30, 30),
        )
        # choose random action until it's valid
        while True:
            d_tank, d_distance = random.choice(actions)
            if tank + d_tank >= 0:
                if self.lip:
                    print('\nTime: %d' % data.step)
                    if d_tank > 0:
                        print('>>> Buying %d L of a fuel' % d_tank)
                    elif d_distance:
                        print('>>> Travelling %d km' % d_distance)
                    else:
                        print('>>> Having some rest')

                return (
                    tank + d_tank,
                    money - data.gas_price*d_tank,
                    distance + d_distance/data.consumption
                )


class Car(object):
    def __init__(self, driver: BaseAgent):
        self.tank_history = []
        self.distance_history = []
        self.driver = driver
        self.money = 0

    def step(self, data):
        tank, money, distance = self.driver.take_action(
            tank=self.tank,
            money=self.money,
            distance=self.distance,
            data=data,
        )
        self.tank_history.append(tank)
        self.distance_history.append(distance)
        self.money = money

    @property
    def distance(self):
        return self.distance_history[-1] if self.distance_history else 0

    @property
    def tank(self):
        return self.tank_history[-1] if self.tank_history else 0


def show_history(tank, distance):
    # fig, ax = plt.subplots(figsize=(12, 8))
    t = np.arange(0, len(tank))

    fig, axs = plt.subplots(2, 1)
    fig.canvas.set_window_title('RL Driver')
    axs[0].plot(t, tank)
    axs[0].set_title('Tank volume')
    axs[0].set_xlabel('step, t')
    axs[0].set_ylabel('volume, l')
    axs[0].xaxis.set_ticks(t)
    axs[0].grid(True)

    axs[1].plot(t, distance)
    axs[1].set_title('Distance travelled')
    axs[1].set_xlabel('step, t')
    axs[1].set_ylabel('distance, km')
    axs[1].xaxis.set_ticks(t)
    axs[1].grid(True)

    fig.tight_layout()
    plt.show()


def main():
    """
    Simulate our trip containing just 10 steps
    """
    environment = [
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
    driver = RandomActionDriver(lip=True)  # driver loves to talk
    car = Car(driver=driver)
    for i, (gas_price, consumption) in enumerate(environment):
        env_data = EnvData(
            step=i,
            gas_price=gas_price,
            consumption=consumption,
        )
        car.step(env_data)

    print('We have driven %d km' % car.distance)
    show_history(tank=car.tank_history, distance=car.distance_history)


if __name__ == '__main__':
    main()
