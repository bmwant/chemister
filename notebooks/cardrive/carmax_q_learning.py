import math
from itertools import count

import numpy as np

from notebooks.cardrive.carmax import BaseAgent, play_trip
from notebooks.cardrive.carmax import ACTIONS, IDLE_ACTION, ENVIRONMENT


s_A = len(ACTIONS)  # actions space size


class Agent(object):
    @classmethod
    def get_available_actions(cls, state):
        step = state // len(ACTIONS)
        tank = 10 * (state % len(ACTIONS))
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
        step = state // s_A
        tank = 10 * (state % len(ACTIONS))
        price, consumption = ENVIRONMENT[step]
        d_tank, d_distance = ACTIONS[action]
        money_spent = d_tank * price
        distance_travelled = d_distance  # d_distance / consumption
        # we want less money to be spent
        norm = math.log(money_spent) if money_spent > math.e else 1
        reward = d_distance / norm
        if step + 1 == len(ENVIRONMENT):
            return (reward, None) if d_distance else (-1, None)

        tank_offset = (tank + d_tank) // 10
        new_state = (step + 1)*s_A + tank_offset
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


def value_iteration():
    actions_space_size = len(ACTIONS)
    s_S = len(ENVIRONMENT) * 7  # states space size, timesteps * tank volumes
    # Initialize array V arbitrarily (0 for all s in S)
    v = np.zeros(s_S)
    gamma = 0.9  # discount factor, should be close to 1 in our case

    def get_outcomes_for_state(s, v):
        """
        Calculate values after performing all actions in a given state
        """
        available_actions = Agent.get_available_actions(s)
        outcomes = np.zeros(s_A)
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
            delta = max(delta, v_ - v[s])

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
    s_S = len(ENVIRONMENT) * 7
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
        outcomes = np.zeros(s_A)
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


if __name__ == '__main__':
    # value_iteration()
    # policy_iteration()
    # value_iteration_play()
    policy_iteration_play()
