import math
import random
from itertools import count
from typing import Tuple

import numpy as np
from matplotlib import pyplot as plt

from notebooks.cardrive.carmax import BaseAgent, play_trip
from notebooks.cardrive.carmax import ACTIONS, IDLE_ACTION, ENVIRONMENT


s_A = len(ACTIONS)  # actions space size
s_T = 7 # states of tank: 0, 10, 20, 30, 40, 50, 60 L
s_S = len(ENVIRONMENT) * s_T  # states space size `step` X `tank`


class Agent(object):
    @classmethod
    def to_state(cls, *, step: int, tank: int) -> int:
        assert tank % 10 == 0
        return step * s_T + tank // 10

    @classmethod
    def from_state(self, state: int) -> Tuple[int, int]:
        step = state // s_T
        tank = 10 * (state % s_T)
        return step, tank

    @classmethod
    def get_available_actions(cls, state):
        _, tank = cls.from_state(state)
        actions = []

        for a, (d_tank, d_distance) in enumerate(ACTIONS):
            if 0 <= tank + d_tank <= 60:
                actions.append(a)

        return actions

    @classmethod
    def get_action_reward(cls, action, state):
        """
        Assuming actions is valid for a given state calculate a reward for it
        """
        # sanity check
        actions = cls.get_available_actions(state)
        if action not in actions:
            raise RuntimeError(f'{action} is not valid for {state}')

        step, tank = cls.from_state(state)
        price, consumption = ENVIRONMENT[step]
        d_tank, d_distance = ACTIONS[action]
        money_spent = d_tank * price
        distance_travelled = d_distance  # d_distance / consumption
        # we want less money to be spent
        norm = math.log(money_spent) if money_spent > math.e else 1
        # reward = d_distance / norm
        # not counting money spent here
        reward = d_distance if d_distance else d_tank/10
        # this will not converge as good as the version above
        # reward = d_distance if d_distance else -1
        if step + 1 == len(ENVIRONMENT):
            return (reward, None) if d_distance else (-1, None)

        new_state = cls.to_state(step=step+1, tank=tank+d_tank)
        # print(reward, new_state)
        return reward, new_state


class PolicyBasedDriver(BaseAgent):
    def __init__(self, policy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.policy = policy

    def take_action(self, *, tank, money, distance, data) -> int:
        step = data.step
        state = step*s_A + tank // 10
        action = int(self.policy[state])
        return action


def value_iteration_play():
    policy = value_iteration()
    driver = PolicyBasedDriver(policy=policy, lip=True)
    play_trip(agent=driver, verbose=True)


def policy_iteration_play():
    policy = policy_iteration()
    driver = PolicyBasedDriver(policy=policy, lip=True)
    play_trip(agent=driver, verbose=True)


def q_learning_play():
    policy = q_learning(plot_chart=False)
    driver = PolicyBasedDriver(policy=policy, lip=True)
    play_trip(agent=driver, verbose=True)


def sarsa_play():
    policy = sarsa(plot_chart=False)
    driver = PolicyBasedDriver(policy=policy, lip=True)
    play_trip(agent=driver, verbose=True)


def value_iteration():
    # Initialize array V arbitrarily (0 for all s in S)
    v = np.zeros(s_S)
    gamma = 0.9  # discount factor, should be close to 1 in our case

    def get_outcomes_for_state(s, v):
        """
        Calculate values after performing all actions in a given state
        """
        available_actions = Agent.get_available_actions(s)
        outcomes = np.full(s_A, -np.inf)
        p = 1 / len(available_actions)
        for a in available_actions:
            reward, new_state = Agent.get_action_reward(a, s)
            if new_state is None:  # s is terminal
                v_ = 0
            else:
                v_ = v[new_state]
            outcomes[a] = p*(reward + gamma * v_)
        return outcomes

    theta = 0.05  # a small positive number
    for i in count():
        delta = 0
        print(f'Iteration {i}...')
        for s in range(s_S):
            v_ = v[s]
            actions_outcomes = get_outcomes_for_state(s, v)
            v[s] = max(actions_outcomes)
            delta = max(delta, np.abs(v_ - v[s]))

        if delta < theta:
            print('Value function converged')
            break

    print('Value function', v)
    # Output a deterministic policy, pi
    def extract_policy(v):
        policy = np.zeros(s_S)
        for s in range(s_S):
            action = np.argmax(get_outcomes_for_state(s, v))
            policy[s] = action
        return policy

    policy = extract_policy(v)
    print('Policy', policy)
    return policy


def policy_iteration():
    v = np.zeros(s_S)  # value function
    # policy, do nothing by default for all states
    p = np.full(s_S, IDLE_ACTION)
    gamma = 0.9  # discount factor

    def get_new_value_for_state(s, v, p):
        """
        Calculates value when following policy `p` from given state `s`
        """
        action = p[s].astype('int')  # to native python type
        reward, new_state = Agent.get_action_reward(action, s)
        v_ = 0 if new_state is None else v[new_state]
        # probability equals 1
        return reward + gamma * v_

    def get_max_action_for_state(s, v):
        """
        Returns the best action which maximizes `v` for state `s`
        """
        available_actions = Agent.get_available_actions(s)

        p = 1 / len(available_actions)
        outcomes = np.full(s_A, -np.inf)
        for a in available_actions:
            reward, new_state = Agent.get_action_reward(a, s)
            v_ = 0 if new_state is None else v[new_state]
            outcomes[a] = p*(reward + gamma * v_)

        return np.argmax(outcomes)

    theta = 0.01
    for i in count():

        print(f'Iteration {i}...')
        while True:
            # policy evaluation
            print('Policy evaluation...')
            delta = 0
            for s in range(s_S):
                v_ = v[s]
                # when following current policy p
                v[s] = get_new_value_for_state(s, v, p)
                delta = max(delta, np.abs(v_ - v[s]))

            if delta < theta:
                break

        # policy improvement
        print('Policy improvement...')
        policy_stable = True
        for s in range(s_S):
            action = p[s]
            p[s] = get_max_action_for_state(s, v)
            if action != p[s]:
                policy_stable = False

        if policy_stable:
            print('Found stable policy!')
            break

    print('Policy', p)
    return p


def print_Q(Q):
    from notebooks.tables import Table

    data = []
    for row in Q:
        data.append(['{:>4.2f}'.format(r) for r in row])

    t = Table(data=data)
    t.print()


def build_evaluation_chart(data, period):
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.canvas.set_window_title('Q-function evaluation')
    datax = np.arange(0, period*len(data), period)
    plt.plot(datax, data, 'b', label='Score')

    ax.legend()
    plt.xlabel('Iterations')
    plt.ylabel('Fitness')
    plt.title('Learning curve')
    ax.grid(True)

    plt.show()


def q_learning(plot_chart=True):
    """
    https://medium.freecodecamp.org/an-introduction-to-q-learning-reinforcement-learning-14ac0b4493cc
    https://www.cse.unsw.edu.au/~cs9417ml/RL1/algorithms.html
    """
    alpha = 0.2  # learning rate
    gamma = 0.9  # discount factor
    Q = np.zeros(shape=(s_S, s_A))

    def maximize_Q(s):
        """
        Maximum expected future reward given the new state `s` and all
        possible actions in this state.
        """
        if s is None:
            return 0
        available_actions = Agent.get_available_actions(s)
        outcomes = []
        for a in available_actions:
            r, s_ = Agent.get_action_reward(a, s)
            outcomes.append(np.max(Q[s_]))
        return np.max(outcomes)

    def extract_policy(Q):
        p = np.full(s_S, -1)
        for s in range(s_S):
            actions = Agent.get_available_actions(s)  # get valid actions
            # get best possible action for a given state
            for a in np.flip(np.argsort(Q[s])):
                if a in actions:
                    p[s] = a
                    break
        return p

    def evaluate_policy(p):
        driver = PolicyBasedDriver(policy=p, lip=False)
        fitness = play_trip(agent=driver, verbose=False)
        return fitness

    # vars for e-greedy action selection strategy
    eps = 0.4  # a bit more exploitation than exploration

    def get_next_action(Q, s, eps=1.0):
        actions = Agent.get_available_actions(s)
        if np.random.random() < eps:
            return np.random.choice(actions)
        else:
            policy = extract_policy(Q)
            return policy[s]

    EPOCHS = 2000
    period = 100  # evaluate each number of epochs
    data = []
    for i in range(EPOCHS):
        if i % period == 0:
            print(f'Evaluating policy on {i} iteration...')
            # collect data for evaluation chart
            p = extract_policy(Q)
            fitness = evaluate_policy(p)
            data.append(fitness)

        s = 0  # starting state
        # running an episode until terminal state reached
        while s is not None:  
            # exploration vs exploitation
            a = get_next_action(Q, s, eps=eps)

            # perform action chosen, receive reward and new state
            r, s_ = Agent.get_action_reward(a, s)
            max_q = maximize_Q(s_)
            Q[s, a] = alpha*(r + gamma*max_q - Q[s, a])

            s = s_

    p = extract_policy(Q)
    print_Q(Q)
    print('Policy', p)
    if plot_chart:
        build_evaluation_chart(data, period=period)
    return p


def sarsa(plot_chart=True):
    alpha = 0.1
    gamma = 0.9

    Q = np.zeros(shape=(s_S, s_A))

    def extract_policy(Q):
        p = np.full(s_S, -1)
        for s in range(s_S):
            actions = Agent.get_available_actions(s)  # get valid actions
            # get best possible action for a given state
            for a in np.flip(np.argsort(Q[s])):
                if a in actions:
                    p[s] = a
                    break
        return p

    def evaluate_policy(p):
        driver = PolicyBasedDriver(policy=p, lip=False)
        fitness = play_trip(agent=driver, verbose=False)
        return fitness

    def get_next_action(Q, s, eps=1.0):
        policy = extract_policy(Q)
        if np.random.random() < eps:
            # explore
            actions = Agent.get_available_actions(s)
            a = np.random.choice(actions)
            return a
        else:
            # exploit
            return int(policy[s])

    # vars for e-greedy action selection strategy
    min_eps = 0.01
    eps = 1.0  # start with exploration
    max_eps = 1.0
    decay_rate = 0.001

    EPOCHS = 2000
    period = 100
    data = []
    for i in range(EPOCHS):
        if i % period == 0:
            print(f'Evaluating policy on {i} iteration...')
            p = extract_policy(Q)
            fitness = evaluate_policy(p)
            data.append(fitness)

        s = 0
        # start each episode from a random action
        a = get_next_action(Q, s, eps=eps)
        while True:  # rollout
            r, s_ = Agent.get_action_reward(a, s)

            if s_ is not None:
                a_ = get_next_action(Q, s_, eps=eps)
                q_update = alpha * (r + gamma*Q[s_, a_] - Q[s, a])
            else:
                # just a reward, no futher state is available
                q_update = alpha * (r - Q[s, a])
                # the is no next action
                a_ = None

            Q[s, a] += q_update 
            s = s_
            a = a_

            if s is None:  # reached terminal state
                break
        # exploit more with each iteration
        eps = min_eps + (max_eps - min_eps)*np.exp(-decay_rate*i)

    policy = extract_policy(Q)
    print_Q(Q)
    print('Policy', policy)
    if plot_chart:
        build_evaluation_chart(data, period=period)
    return policy


if __name__ == '__main__':
    # value_iteration()
    # policy_iteration()
    # value_iteration_play()
    # policy_iteration_play()
    # q_learning()
    # q_learning_play()
    # sarsa()
    sarsa_play()
