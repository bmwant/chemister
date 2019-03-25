import os
from collections import Counter

import numpy as np

from notebooks.algo.agent import ACTIONS
from notebooks.algo.environment import Environment
from notebooks.algo.agent import PolicyBasedTrader, s_W

MODEL_FILENAME = 'policy_iteration04.model'


def save_model(v):
    # print('\nSaving model to a file {}'.format(MODEL_FILENAME))
    with open(MODEL_FILENAME, 'wb') as f:
        np.save(f, v)


def load_model():
    if os.path.exists(MODEL_FILENAME):
        print('\nLoading model from {}'.format(MODEL_FILENAME))
        with open(MODEL_FILENAME, 'rb') as f:
            return np.load(f)


def get_max_action_for_state(agent, s, v, gamma=1.0):
    """
    Return action index for which we can get maximum expected reward when
    being in a state `s` for the value function `v`.
    """
    actions = agent.get_available_actions(state=s)
    outcomes = np.full(agent.actions_space_size, -np.inf)
    for a in actions:
        r, s_ = agent.take_action(a, s, dry_run=True)
        v_ = 0 if s_ is None else v[s_]
        p = 1
        outcomes[a] = p*(r + gamma*v_)
    return np.argmax(outcomes)


def extract_policy(agent, v):
    print('Extracting policy...')
    s_S = agent.states_space_size
    policy = np.full(s_S, -1)
    period = 100
    for state in range(s_S):
        if state % period == 0:
            print(f'Current state: {state}')
        action = get_max_action_for_state(agent, state, v)
        policy[state] = action
    return policy


def main():
    v = load_model()
    env = Environment()
    env.load(2018)
    # env.load_demo()
    # agent = PolicyBasedTrader(policy=None, env=env, verbose=False)
    # policy = extract_policy(agent, v)
    # print('Count actions')

    actions_performed = {30: 16221, 4: 4698, 5: 4165, 25: 3937, 0: 3134, 2: 783, 15: 759, 3: 758, 1: 747, 10: 713, 20: 678, 9: 47, 26: 35, 14: 35, 27: 26, 19: 25, 8: 23, 21: 21, 13: 16, 7: 13, 16: 10, 22: 8, 28: 8, 12: 4, 17: 1}
    for i, action in enumerate(ACTIONS):
        print(action, '->', actions_performed.get(i))


    # for step in range(env.size):
    #     state = agent.to_state(step, agent.amount_usd)
    #     action = policy[state]
    #     agent.take_action(action, state)

    # print('End amount UAH: {:.2f}'.format(agent.amount_uah))
    # print('End amount USD: {:.2f}'.format(agent.amount_usd))
    # print('Profit in UAH: {:.2f}'.format(agent.profit))
    # exit_uah = agent.amount_usd * env.get_observation(env.size-1).rate_buy
    # exit_amount = agent.amount_uah + exit_uah
    # print('Amount on exit now: {:.2f}'.format(exit_amount))


if __name__ == '__main__':
    main()
