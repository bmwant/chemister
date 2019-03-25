import os
import sys
import time
import timeit
import concurrent.futures
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from humanfriendly import format_timespan

from notebooks.algo.agent import PolicyBasedTrader, s_W
from notebooks.algo.environment import Environment
from notebooks.cardrive.visualize import build_evaluation_chart


def extract_policy(agent, v):
    s_S = agent.states_space_size
    policy = np.full(s_S, -1)
    for state in range(s_S):
        action = np.argmax(get_outcomes_for_state(agent, state, v))
        policy[state] = action
    return policy


def get_outcomes_for_state(agent, state, v, gamma=1.0):
    actions = agent.get_available_actions(state)
    # print(f'Available actions in state {state} is {actions}')
    # to be able perform np.argmax over it properly
    outcomes = np.full(agent.actions_space_size, -np.inf)
    for a in actions:
        p = 1  # probability of moving to the state `s_`
        # when being in state `state` and taking action `a`
        r, s_ = agent.take_action(a, state, dry_run=True)
        # `r` reward for taking action `a` in the state `state`
        v_ = v[s_] if s_ is not None else 0
        outcomes[a] = p*(r + gamma*v_)

    # print(f'Outcomes are {outcomes}')
    return outcomes


def evaluate_policy(policy):
    env = Environment()
    env.load(2018)
    # env.load_demo()
    agent = PolicyBasedTrader(policy=None, env=env, verbose=True)

    for step in range(env.size):
        state = agent.to_state(step, agent.amount_usd)
        action = policy[state]
        agent.take_action(action, state)

    print('End amount UAH: {:.2f}'.format(agent.amount_uah))
    print('End amount USD: {:.2f}'.format(agent.amount_usd))
    print('Profit in UAH: {:.2f}'.format(agent.profit))
    exit_uah = agent.amount_usd * env.get_observation(env.size-1).rate_buy
    exit_amount = agent.amount_uah + exit_uah
    print('Amount on exit now: {:.2f}'.format(exit_amount))
    return agent.profit


def print_value_function(v):
    print('='*80)
    print('Value function')

    for row in range(len(v)):
        print('{:.2f}\t'.format(v[row]), end=' ')
        if (row+1) % s_W == 0:
            print()


MODEL_FILENAME = 'value_iteration04.model'


def save_model(v):
    # print('\nSaving model to a file {}'.format(MODEL_FILENAME))
    with open(MODEL_FILENAME, 'wb') as f:
        np.save(f, v)


def load_model():
    if os.path.exists(MODEL_FILENAME):
        print('\nLoading model from {}'.format(MODEL_FILENAME))
        with open(MODEL_FILENAME, 'rb') as f:
            return np.load(f)


def value_iteration(plot_chart=False):
    env = Environment()
    env.load(2018)
    # env.load_demo()
    agent = PolicyBasedTrader(policy=None, env=env)
    s_S = agent.states_space_size
    s_A = agent.actions_space_size

    v = load_model()
    v = v if v is not None else np.zeros(s_S)
    gamma = 1  # undiscounted return for the whole episode

    EPOCHS = 20
    period = 5
    data = []

    print(f'States space size is {s_S}')
    print(f'Actions space size is {s_A}')
    print(f'Max epochs to run {EPOCHS}')

    theta = 0.05  # convergence check
    t1 = timeit.default_timer()
    for i in range(EPOCHS):
        delta = 0
        t2 = timeit.default_timer()
        dt = format_timespan(t2-t1)
        sys.stdout.write(f'\rIteration {i}/{EPOCHS}... {dt} passed')
        sys.stdout.flush()
        for s in range(s_S):
            v_ = v[s]
            actions_outcomes = get_outcomes_for_state(
                agent, s, v, gamma=gamma)
            v[s] = max(actions_outcomes)
            delta = max(delta, np.abs(v_ - v[s]))

        if i % period == 0:
            save_model(v)

        if delta < theta:
            print(f'\nValue function converged in {i} iterations')
            print(
                '\nSaving resulting model to a file {}'.format(MODEL_FILENAME))
            save_model(v)
            break

    print_value_function(v)

    print('='*80)
    print('Extracting deterministic policy, pi')
    policy = extract_policy(agent, v)
    print(policy)

    return policy


def main():
    t1 = timeit.default_timer()
    policy = value_iteration()
    t2 = timeit.default_timer()
    dt = format_timespan(t2-t1)
    print('\nValue iteration finished in {}'.format(dt))
    print('='*80)
    print('Evaluating extracted policy')
    evaluate_policy(policy)


if __name__ == '__main__':
    main()
