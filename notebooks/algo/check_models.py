import os
from collections import Counter

import numpy as np

from notebooks.helpers import hldit
from notebooks.algo.agent import ACTIONS
from notebooks.algo.environment import Environment
from notebooks.algo.agent import PolicyBasedTrader, s_W

MODEL_FILENAME = 'policy_iteration04.model'
POLICY_FILENAME = 'policy_dump.model'


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


@hldit
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
    agent = PolicyBasedTrader(policy=None, env=env, verbose=False)
    print(f'Total states: {agent.states_space_size}')
    # policy = extract_policy(agent, v)
    with open(POLICY_FILENAME, 'rb') as f:
        policy = np.load(f)

    print('Count actions')
    c = Counter()
    agent = PolicyBasedTrader(policy=None, env=env, verbose=True)

    min_amount_uah = 0
    for step in range(env.size):
        state = agent.to_state(step, agent.amount_usd)
        action = policy[state]
        c[action] += 1
        agent.take_action(action, state)
        min_amount_uah = min(agent.amount_uah, min_amount_uah)

    for i, action in enumerate(ACTIONS):
        print(action, '->', c.get(i))

    print('min amount uah', min_amount_uah)
    print(c)
    # print('End amount UAH: {:.2f}'.format(agent.amount_uah))
    # print('End amount USD: {:.2f}'.format(agent.amount_usd))
    # print('Profit in UAH: {:.2f}'.format(agent.profit))
    # exit_uah = agent.amount_usd * env.get_observation(env.size-1).rate_buy
    # exit_amount = agent.amount_uah + exit_uah
    # print('Amount on exit now: {:.2f}'.format(exit_amount))


if __name__ == '__main__':
    main()
