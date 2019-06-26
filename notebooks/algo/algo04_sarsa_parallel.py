import os
import time
import pickle
import argparse
import threading
import concurrent.futures
from threading import Lock
from concurrent.futures import ThreadPoolExecutor

import tqdm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation

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


def evaluate_q(env, Q):
    agent = PolicyBasedTrader(policy=None, env=env)
    policy = extract_policy(agent, Q)

    for step in range(env.size):
        state = agent.to_state(step, agent.amount_usd)
        action = policy[state]
        agent.take_action(action, state)

    return agent.profit


DUMP_FILENAME = 'sarsa_q.model'


class SarsaModel(object):
    def __init__(self, Q, eps):
        self.Q = Q
        self.eps = eps

    def save(self):
        print('\nSaving model to a file {}'.format(DUMP_FILENAME))
        with open(DUMP_FILENAME, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load():
        if os.path.exists(DUMP_FILENAME):
            print('Loading model from {}'.format(DUMP_FILENAME))
            with open(DUMP_FILENAME, 'rb') as f:
                return pickle.load(f)


def evaluate_agent():
    env = Environment()
    env.load(2018)
    agent = PolicyBasedTrader(policy=None, env=env)
    model = SarsaModel.load()
    if model is None:
        raise RuntimeError('Train agent first, no model to load')

    policy = extract_policy(agent, model.Q)

    print('Evaluate SARSA model on env with size: {}'.format(env.size))
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


def sarsa(play=False, plot_chart=False):
    env = Environment()
    # load smaller environment for just one month
    env.load(2018)
    agent = PolicyBasedTrader(policy=None, env=env)
    s_S = agent.states_space_size
    s_A = agent.actions_space_size
    print(f'States space size is {s_S}')
    print(f'Actions space size is {s_A}')
    print(f'Steps in environment is {env.size}')

    alpha = 1  # learning rate, discard old results immediately
    gamma = 1  # discount factor
    # load model from a file if saved previously
    model = SarsaModel.load() if play else None
    Q = model.Q if model is not None else np.zeros(shape=(s_S, s_A))
    if model is not None:
        print(f'Resuming with eps={model.eps}')

    min_eps = 0.01
    # eps = 0.1  # start with exploration
    eps = model.eps if model is not None else 0.1
    max_eps = 1.0
    decay_rate = 0.01

    EPOCHS = 100
    period = 5
    data = []

    print(f'Running {EPOCHS} epochs\n')
    lock = Lock()

    def run_iterations(worker_num=0):
        # print(f'#{worker_num}: Running {EPOCHS} iterations in worker')
        nonlocal eps
        progress = tqdm.tqdm(
            desc='#{:02d}'.format(worker_num),
            position=worker_num,
            total=EPOCHS,
            leave=False,
        )
        for i in range(EPOCHS):
            Q_copy = Q.copy()  # do not lock, just evaluate on a recent copy
            if i % period == 0:
                # print(f'#{worker_num}: Evaluating agent on {i} iteration...')
                fitness = evaluate_q(env, Q_copy)
                data.append(fitness)

            # reset env for each epoch
            agent = PolicyBasedTrader(policy=None, env=env)
            s = 0  # starting state
            a = get_next_action(agent, Q_copy, s, eps=eps)
            # print(f'#{worker_num}: Rollout for epoch {i}')
            while s is not None:  # rollout
                r, s_ = agent.take_action(a, s)
                with lock:
                    if s_ is not None:
                        a_ = get_next_action(agent, Q, s_, eps=eps)
                        q_update = alpha * (r + gamma*Q[s_, a_] - Q[s, a])
                    else:
                        q_update = alpha * (r - Q[s, a])
                        a_ = None

                    Q[s, a] += q_update

                s = s_
                a = a_
            eps = min_eps + (max_eps - min_eps)*np.exp(-decay_rate*i)
            progress.update()
        progress.close()
        return worker_num

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.canvas.set_window_title('Agent evaluation')

    def build_live_chart(i):
        local_data = data[::]
        datax = np.arange(0, period*len(local_data), period)

        plt.xlabel('Iterations')
        plt.ylabel('Fitness')
        plt.title('Learning curve')
        ax.clear()
        ax.plot(datax, local_data, 'b', label='Score')
        ax.legend()
        ax.grid(True)

    workers = 1
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(run_iterations, i)
            for i in range(workers)
        ]
        ani = animation.FuncAnimation(fig, build_live_chart, interval=500)
        plt.show()
        result = concurrent.futures.wait(futures)
        plt.close()
        assert len(result.done) == workers

    # Save latest data
    if not play:
        model = SarsaModel(Q=Q, eps=eps)
        model.save()
    print('\nDone!')
    policy = extract_policy(agent, Q)

    if plot_chart:
        build_evaluation_chart(data, period=period)

    return policy


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--play',
        action='store_true',
        default=False,
        help='use saved model just to evaluate an agent',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(args.play)
    sarsa(plot_chart=False)
    evaluate_agent()


if __name__ == '__main__':
    main()
