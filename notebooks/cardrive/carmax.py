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
        self.fund_history = []
        self.driver = driver

    def step(self, data):
        tank, money, distance = self.driver.take_action(
            tank=self.tank,
            money=self.money,
            distance=self.distance,
            data=data,
        )
        self.tank_history.append(tank)
        self.distance_history.append(distance)
        self.fund_history.append(money)

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
    print('We have spent %.2f$' % car.money)
    show_history(
        tank=car.tank_history, 
        distance=car.distance_history,
        money=car.fund_history,
    )


if __name__ == '__main__':
    main()
