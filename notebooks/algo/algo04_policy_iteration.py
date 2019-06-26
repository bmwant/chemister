import os
import sys
import time
import timeit
import concurrent.futures
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from humanfriendly import format_timespan

from notebooks.algo.agent import PolicyBasedTrader, IDLE_ACTION_INDEX
from notebooks.algo.agent import s_W
from notebooks.algo.environment import Environment
from notebooks.cardrive.visualize import build_evaluation_chart


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


def get_new_value_for_state(agent, s, v, p, gamma=1.0):
    """
    Get reward when following current policy `p` and being in the state `s` for
    current value function `v`.
    """
    action = p[s].astype('int')
    r, s_ = agent.take_action(action, s, dry_run=True)
    v_ = 0 if s_ is None else v[s_]
    return r + gamma * v_


def print_value_function(v):
    print('='*80)
    print('Value function')

    for row in range(len(v)):
        print('{:.2f}\t'.format(v[row]), end=' ')
        if (row+1) % s_W == 0:
            print()


def evaluate_policy(policy, verbose=False):
    env = Environment()
    env.load(2018)
    # env.load_demo()
    agent = PolicyBasedTrader(policy=None, env=env, verbose=True)

    for step in range(env.size):
        state = agent.to_state(step, agent.amount_usd)
        action = policy[state]
        r, s_ = agent.take_action(action, state)
        if verbose:
            print(f'Transition {state}->{s_}')

    print('End amount UAH: {:.2f}'.format(agent.amount_uah))
    print('End amount USD: {:.2f}'.format(agent.amount_usd))
    print('Profit in UAH: {:.2f}'.format(agent.profit))
    exit_uah = agent.amount_usd * env.get_observation(env.size-1).rate_buy
    exit_amount = agent.amount_uah + exit_uah
    print('Amount on exit now: {:.2f}'.format(exit_amount))
    return agent.profit


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


def policy_iteration():
    env = Environment()
    env.load(2018)
    # env.load_demo()
    agent = PolicyBasedTrader(policy=None, env=env)
    s_S = agent.states_space_size
    s_A = agent.actions_space_size

    v = load_model()
    v = v if v is not None else np.zeros(s_S)  # value function
    p = np.full(s_S, IDLE_ACTION_INDEX)  # initial policy should be valid
    gamma = 1  # discount factor

    EPOCHS = 1000
    period = 5
    data = []

    print(f'States space size is {s_S}')
    print(f'Actions space size is {s_A}')
    print(f'Max epochs to run {EPOCHS}')

    theta = 0.05  # convergence check
    t1 = timeit.default_timer()
    for i in range(EPOCHS):
        t2 = timeit.default_timer()
        dt = format_timespan(t2-t1)
        sys.stdout.write(f'\rIteration {i}/{EPOCHS}... {dt} passed')
        sys.stdout.flush()
        while True:  # policy evaluation
            delta = 0
            for s in range(s_S):
                v_ = v[s]
                v[s] = get_new_value_for_state(agent, s, v, p, gamma=gamma)
                delta = max(delta, np.abs(v_ - v[s]))

            # print(delta)
            if delta < theta:
                break

        policy_stable = True
        # policy improvement
        for s in range(s_S):
            action = p[s]
            p[s] = get_max_action_for_state(agent, s, v, gamma=gamma)
            if action != p[s]:
                policy_stable = False

        if i % period == 0:
            save_model(v)

        if policy_stable:
            print(f'\nFound stable policy on iteration {i}!')
            print(
                '\nSaving resulting model to a file {}'.format(MODEL_FILENAME))
            save_model(v)
            break

    print_value_function(v)

    return p


def main():
    t1 = timeit.default_timer()
    policy = policy_iteration()
    t2 = timeit.default_timer()
    dt = format_timespan(t2-t1)
    print('\nPolicy iteration finished in {}'.format(dt))
    print('='*80)
    print('Evaluating extracted policy')
    evaluate_policy(policy)


def test():
    policy = np.array([
        1, 3, 3, 3, 1, 3, 3, 3, 2, 3, 2, 3
    ]) 
    evaluate_policy(policy, verbose=True)


if __name__ == '__main__':
    main()
    # test()
