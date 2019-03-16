import os
import time
import concurrent.futures
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from notebooks.algo.agent import PolicyBasedTrader
from notebooks.algo.environment import Environment
from notebooks.cardrive.visualize import build_evaluation_chart


def extract_policy(agent, Q):
    s_S = agent.states_space_size
    policy = np.full(s_S, -1)
    for state in range(s_S):
        # valid actions in a given state
        actions = agent.get_available_actions(state)
        for a in np.flip(np.argsort(Q[state])):  # from best to worst
            if a in actions:
                policy[state] = a
                break
    return policy


def get_next_action(agent, Q, state, eps=1.0) -> int:
    """
    desc.
    """
    actions = agent.get_available_actions(state)
    if np.random.random() < eps:
        return np.random.choice(actions)
    else:
        policy = extract_policy(agent, Q)
        return int(policy[state])


def maximize_q(agent, Q, state):
    """
    One step lookahead for the best action which maximizes Q in a new state.
    """
    if state is None:
        return 0

    # valid actions in a given state
    actions = agent.get_available_actions(state)
    outcomes = []
    for a in actions:
        r, s_ = agent.take_action(a, state, dry_run=True)
        outcomes.append(np.max(Q[s_]))
    return np.max(outcomes)


def evaluate_q(env, Q):
    agent = PolicyBasedTrader(policy=None, env=env)
    policy = extract_policy(agent, Q)

    for step in range(env.size):
        state = agent.to_state(step, agent.amount_usd)
        action = policy[state]
        agent.take_action(action, state)

    return agent.profit


def evaluate_agent():
    env = Environment()
    env.load(2018)
    agent = PolicyBasedTrader(policy=None, env=env)
    model = load_model()
    if model is None:
        raise RuntimeError('Train agent first, no model to load')

    policy = extract_policy(agent, model)

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


DUMP_FILENAME = 'q_learning.model'


def save_model(Q):
    print('\nSaving model to a file {}'.format(DUMP_FILENAME))
    with open(DUMP_FILENAME, 'wb') as f:
        np.save(f, Q)


def load_model():
    if os.path.exists(DUMP_FILENAME):
        print('Loading model from {}'.format(DUMP_FILENAME))
        with open(DUMP_FILENAME, 'rb') as f:
            return np.load(f)


def q_learning(plot_chart=False):
    env = Environment()
    env.load(2018)
    agent = PolicyBasedTrader(policy=None, env=env)
    s_S = agent.states_space_size
    s_A = agent.actions_space_size
    print(f'States space size is {s_S}')
    print(f'Actions space size is {s_A}')

    alpha = 0.2  # learning rate
    gamma = 0.9  # discount factor
    eps = 0.4  # exploration factor
    model = load_model()
    Q = model if model is not None else np.zeros(shape=(s_S, s_A))

    EPOCHS = 1000
    period = 5
    data = []

    lock = Lock()

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

    workers = 8
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(run_iterations, i): i
            for i in range(workers)
        }
        for future in concurrent.futures.as_completed(futures):
            worker_num = futures[future]
            try:
                r = future.result()
                print(f'#{worker_num}: Finished!')
            except Exception as e:
                print(f'#{worker_num}: Failed with {e}')

    save_model(Q)
    policy = extract_policy(agent, Q)
    if plot_chart:
        build_evaluation_chart(data, period=period)

    return policy


if __name__ == '__main__':
    q_learning(plot_chart=True)
    evaluate_agent()
