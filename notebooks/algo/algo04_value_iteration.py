import os
import sys
import time
import concurrent.futures
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from notebooks.algo.agent import PolicyBasedTrader
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
    # to be able perform np.argmax over it properly
    outcomes = np.full(agent.actions_space_size, -np.inf)
    p = 1 / len(actions)  # all actions are equally available
    for a in actions:
        r, s_ = agent.take_action(a, state, dry_run=True)
        v_ = v[s_] if s_ is not None else 0
        outcomes[a] = p*(r + gamma*v_)

    return outcomes


def evaluate_policy(policy):
    env = Environment()
    # env.load(2018)
    env.load_demo()
    agent = PolicyBasedTrader(policy=None, env=env, verbose=True)

    print(policy)
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


def value_iteration(plot_chart=False):
    env = Environment()
    # env.load(2018)
    env.load_demo()
    agent = PolicyBasedTrader(policy=None, env=env)
    s_S = agent.states_space_size
    s_A = agent.actions_space_size
    print(f'States space size is {s_S}')
    print(f'Actions space size is {s_A}')

    v = np.zeros(s_S)
    gamma = 0.99  # discount factor

    EPOCHS = 10
    period = 5
    data = []

    lock = Lock()

    theta = 0.05  # convergence check
    for i in range(EPOCHS):
        delta = 0
        sys.stdout.write(f'\rIteration {i}/{EPOCHS}...')
        sys.stdout.flush()
        for s in range(s_S):
            v_ = v[s]
            actions_outcomes = get_outcomes_for_state(agent, s, v, gamma=gamma)
            v[s] = max(actions_outcomes)
            delta = max(delta, np.abs(v_ - v[s]))

        if delta < theta:
            print('Value function converged')
            break
    def run_iterations(worker_num=0):
        print(f'#{worker_num}: Running {EPOCHS} iterations in worker')
        for i in range(EPOCHS):
            Q_copy = Q.copy()  # do not lock, just evaluate on a recent copy 
            if i % period == 0:
                print(f'#{worker_num}: Evaluating agent on {i} iteration...')
                fitness = evaluate_q(env, Q_copy)
                print(f'#{worker_num}: Current fitness: {fitness:.2f}')
                data.append(fitness)

            # reset env for each epoch
            agent = PolicyBasedTrader(policy=None, env=env)
            s = 0  # starting state
            print(f'#{worker_num}: Rollout for epoch {i}')
            while s is not None:  # rollout
                # do not allow other threads to update Q within a single step
                with lock:  
                    a = get_next_action(agent, Q, s, eps) 

                    r, s_ = agent.take_action(a, s)
                    # maximize Q for the next state
                    max_q = maximize_q(agent, Q, s_)  

                    Q[s, a] = alpha*(r + gamma*max_q - Q[s, a])
                
                s = s_

    print('Extracting deterministic policy, pi')
    policy = extract_policy(agent, v)
    print('Evaluating extracted policy')
    evaluate_policy(policy)
    return policy


if __name__ == '__main__':
    value_iteration(plot_chart=True)
