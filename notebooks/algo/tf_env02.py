import abc
import argparse

import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tf_agents.agents.dqn import q_network, dqn_agent
from tf_agents.environments import (
    trajectory,
    py_environment,
    tf_environment,
    tf_py_environment,
    wrappers,
    suite_gym,
    utils,
)
from tf_agents.networks import q_rnn_network
from tf_agents.environments import time_step as ts
from tf_agents.policies import (
    random_tf_policy,
    greedy_policy,
    epsilon_greedy_policy,
    tf_py_policy,
)
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.utils import common
from tf_agents.specs import array_spec

from notebooks.algo.tf_policy import (
    DummyTradePolicy, 
    FilteredQPolicy,
    FilteredRandomPyPolicy,
    FilteredRandomTFPolicy,
)
from notebooks.algo.agent import PolicyBasedTrader as Agent
from notebooks.helpers import load_year_dataframe, DATE_FMT


tf.compat.v1.enable_v2_behavior()
FLAGS = None
VERBOSE = False
MAX_AMOUNT = 1000
# WRONG_ACTION_REWARD = -MAX_AMOUNT*50 
WRONG_ACTION_REWARD = -100


class TradeEnvironment(py_environment.PyEnvironment):
    def __init__(self):
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32,
            minimum=0,
            maximum=MAX_AMOUNT,
            name='action',
        )
        # actions = np.arange(0, MAX_AMOUNT+1, 10, dtype=np.int32)
        # print(actions.shape)
        # self._action_spec = array_spec.ArraySpec.from_array(
        #     actions, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(17,), dtype=np.float32,
            # minimum=[0, 0, 0],
            # maximum=[100, 100, MAX_AMOUNT],
            name='observation',
        )
        self._step_num = 0
        self._amount = 0  # amount of currency purchased
        self._episode_ended = False
        self._df = None
        self._load(2018)

    def _load(self, year):
        print('Loading environment for {} year'.format(year))
        self._df = load_year_dataframe(year)
        # just make sure rows are ordered by date
        self._df['date'] = pd.to_datetime(self._df['date'], format=DATE_FMT)

        self._df.sort_values(by=['date'], inplace=True)
        self._df.reset_index(drop=True, inplace=True)
        days = 31
        print('Simplify and run just for {} days'.format(days))
        self._df = self._df.head(days)

    @property
    def env_size(self):
        return len(self._df.index)

    def observation_spec(self):
        return self._observation_spec

    def action_spec(self):
        return self._action_spec

    def _reset(self):
        self._amount = 0
        self._step_num = 0
        self._episode_ended = False
        observation = self._get_observation(0)
        return ts.restart(observation=observation)

    def _get_observation(self, state):
        # step, amount = Agent.from_state(None, state)
        step = self._step_num
        amount = self._amount
        amount_left = MAX_AMOUNT - amount
        if step < self.env_size:
            row = self._df.iloc[[step]]
            buy = row['buy'].item()
            sale = row['sale'].item()
        else:
            # handle termination states
            buy = 0
            sale = 0
        not_nan = lambda x: x if x is not np.nan else 0
        min_buy_week = not_nan(self._df.iloc[step-7:step]['buy'].min())
        min_buy_prev = not_nan(self._df.iloc[:step]['buy'].min())
        max_buy_week = not_nan(self._df.iloc[step-7:step]['buy'].max())
        max_buy_prev = not_nan(self._df.iloc[:step]['buy'].max())
        avg_buy_week = not_nan(self._df.iloc[step-7:step]['buy'].mean())
        avg_buy_prev = not_nan(self._df.iloc[:step]['buy'].mean())
        min_sale_week = not_nan(self._df.iloc[step-7:step]['sale'].min())
        min_sale_prev = not_nan(self._df.iloc[:step]['sale'].min())
        max_sale_week = not_nan(self._df.iloc[step-7:step]['sale'].max())
        max_sale_prev = not_nan(self._df.iloc[:step]['sale'].max())
        avg_sale_week = not_nan(self._df.iloc[step-7:step]['sale'].mean())
        avg_sale_prev = not_nan(self._df.iloc[:step]['sale'].mean())
        observation = np.array(
            [
                min_buy_week,
                min_buy_prev,
                max_buy_week,
                max_buy_prev,
                avg_buy_week,
                avg_buy_prev,
                buy,
                min_sale_week,
                min_sale_prev,
                max_sale_week,
                max_sale_prev,
                avg_sale_week,
                avg_sale_prev,
                sale, 
                amount,
                amount_left,
                step,
            ],
            dtype=np.float32,
        )
        return observation

    def _step(self, action):
        # The last action ended the episode.
        # Ignore the current action and start a new episode
        if self._episode_ended:
            return self.reset()

        action_value = action - MAX_AMOUNT/2 
        step = self._step_num
        amount = self._amount

        row = self._df.iloc[[step]]
        buy = row['buy'].item()
        sale = row['sale'].item()

        reward = 0
        if action_value > 0:  # buying currency
            reward = - sale * action_value
        elif action_value < 0 and amount >= np.abs(action_value):  
            # selling currency
            reward = buy * np.abs(action_value)

        new_amount = amount + action_value
        # take action
        self._step_num += 1

        if self._step_num == self.env_size:
            self._episode_ended = True

        if 0 <= new_amount <= MAX_AMOUNT:
            amount = new_amount
        else:
            raise RuntimeError(
                'Wrong action is produced by policy: {}, {}: a{}, s{}'.format(
                    action, action_value, amount, step))
            reward = WRONG_ACTION_REWARD

        if VERBOSE:
            print(
                '#{step} ({amount}->{new_amount}): '
                '{buy}/{sale}; {action}; {reward}'.format(
                    step=step,
                    amount=self._amount,
                    new_amount=amount,
                    buy=buy,
                    sale=sale,
                    action=action_value,
                    reward=reward,
            ))

        # Update amount after action taken and return the observation
        self._amount = amount
        observation = self._get_observation(step)

        if self._episode_ended:
            return ts.termination(
                observation=observation,
                reward=reward,
            )

        return ts.transition(
            observation=observation,
            reward=reward,
            discount=1.0,
        )


def compute_avg_return(environment, policy, num_episodes=10):
    total_return = 0.0 
    for _ in range(num_episodes):
        time_step = environment.reset()
        print(type(time_step))
        episode_return = 0.0
        while not time_step.is_last():
            action_step = policy.action(time_step)
            time_step = environment.step(action_step.action)
            episode_return += time_step.reward
        total_return += episode_return
    avg_return = total_return / num_episodes
    return avg_return.numpy()[0]


def collect_step(environment, policy):
  time_step = environment.current_time_step()
  action_step = policy.action(time_step)
  next_time_step = environment.step(action_step.action)
  traj = trajectory.from_transition(time_step, action_step, next_time_step)

  return traj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log_dir',
        type=str,
        default='/tmp/tensorflow/logs/tfenv02',
        help='summaries log directory',
    )
    FLAGS, unparsed = parser.parse_known_args()
    if tf.gfile.Exists(FLAGS.log_dir):
        tf.gfile.DeleteRecursively(FLAGS.log_dir)
    tf.gfile.MakeDirs(FLAGS.log_dir)
    train()


def train():
    global VERBOSE
    environment = TradeEnvironment()
    # utils.validate_py_environment(environment, episodes=5)
    # Environments
    train_env = tf_py_environment.TFPyEnvironment(environment)
    eval_env = tf_py_environment.TFPyEnvironment(environment)

    num_iterations = 50
    fc_layer_params = (512, )  # ~ (17 + 1001) / 2
    input_fc_layer_params = (17, )
    output_fc_layer_params = (20, )
    lstm_size = (17, )
    initial_collect_steps = 20
    collect_steps_per_iteration = 1
    batch_size = 64
    replay_buffer_capacity = 10000

    gamma = 0.99  # check if 1 will work here
    target_update_tau = 0.05
    target_update_period = 5
    epsilon_greedy = 0.1
    reward_scale_factor = 1.0
    learning_rate = 1e-2
    log_interval = 30
    num_eval_episodes = 5
    eval_interval = 15

    # q_net = q_network.QNetwork(
    #     train_env.observation_spec(),
    #     train_env.action_spec(),
    #     fc_layer_params=fc_layer_params,
    # )

    q_net = q_rnn_network.QRnnNetwork(
        train_env.observation_spec(),
        train_env.action_spec(),
        input_fc_layer_params=input_fc_layer_params,
        lstm_size=lstm_size,
        output_fc_layer_params=output_fc_layer_params,
    )

    optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate)

    train_step_counter = tf.compat.v2.Variable(0)

    tf_agent = dqn_agent.DqnAgent(
        train_env.time_step_spec(),
        train_env.action_spec(),
        q_network=q_net,
        optimizer=optimizer,
        epsilon_greedy=epsilon_greedy,
        target_update_tau=target_update_tau,
        target_update_period=target_update_period,
        gamma=gamma,
        reward_scale_factor=reward_scale_factor,
        td_errors_loss_fn=dqn_agent.element_wise_squared_loss,
        train_step_counter=train_step_counter,
        gradient_clipping=None,
        debug_summaries=False,
        summarize_grads_and_vars=False,
    )

    q_policy = FilteredQPolicy(
        tf_agent._time_step_spec, 
        tf_agent._action_spec, 
        q_network=tf_agent._q_network,
    )

    # Valid policy to pre-fill replay buffer
    dummy_policy = DummyTradePolicy(
        train_env.time_step_spec(),
        train_env.action_spec(),
    )

    # Main agent's policy; greedy one
    policy = greedy_policy.GreedyPolicy(q_policy)
    filtered_random_py_policy = FilteredRandomPyPolicy(
        time_step_spec=policy.time_step_spec, 
        action_spec=policy.action_spec,
    )
    filtered_random_tf_policy = tf_py_policy.TFPyPolicy(
        filtered_random_py_policy)
    collect_policy = epsilon_greedy_policy.EpsilonGreedyPolicy(
        q_policy, epsilon=tf_agent._epsilon_greedy)
    # Patch random policy for epsilon greedy collect policy

    filtered_random_tf_policy = FilteredRandomTFPolicy(
        time_step_spec=policy.time_step_spec,
        action_spec=policy.action_spec,
    )
    collect_policy._random_policy = filtered_random_tf_policy
    
    tf_agent._policy = policy
    tf_agent._collect_policy = collect_policy
    tf_agent.initialize()
    
    replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
        data_spec=tf_agent.collect_data_spec,
        batch_size=train_env.batch_size,
        max_length=replay_buffer_capacity,
    )
    print(
        'Pre-filling replay buffer in {} steps'.format(initial_collect_steps))
    for _ in range(initial_collect_steps):
        traj = collect_step(train_env, dummy_policy)
        replay_buffer.add_batch(traj)

    dataset = replay_buffer.as_dataset(
        num_parallel_calls=3, sample_batch_size=batch_size, num_steps=2,
    ).prefetch(3)

    iterator = iter(dataset)
    # Train
    tf_agent.train = common.function(tf_agent.train)

    tf_agent.train_step_counter.assign(0)

    avg_return = compute_avg_return(
        eval_env, tf_agent.policy, num_eval_episodes)

    returns = [avg_return]
    
    print('Starting iterations...')
    for i in range(num_iterations):

        # fill replay buffer
        for _ in range(collect_steps_per_iteration):
            traj = collect_step(train_env, tf_agent.collect_policy)
            # Add trajectory to the replay buffer
            replay_buffer.add_batch(traj)

        experience, _ = next(iterator)
        train_loss = tf_agent.train(experience)

        step = tf_agent.train_step_counter.numpy()

        if step % log_interval == 0:
            print('step = {0}: loss = {1}'.format(step, train_loss.loss))

        if step % eval_interval == 0:
            avg_return = compute_avg_return(
                eval_env, tf_agent.policy, num_eval_episodes)
            print('step = {0}: avg return = {1}'.format(step, avg_return))
            returns.append(avg_return)

    print('Finished {} iterations!'.format(num_iterations))

    print('Playing with resulting policy')
    VERBOSE = True
    r = compute_avg_return(eval_env, tf_agent.policy, 1)
    print('Result: {}'.format(r))
    steps = range(0, num_iterations+1, eval_interval)

    # merged = tf.summary.merge_all()
    # writer = tf.summary.FileWriter(FLAGS.log_dir)
    # 
    # writer.close()
    print('Check out chart for learning')
    plt.plot(steps, returns)
    plt.ylabel('Average Return')
    plt.xlabel('Step')
    plt.ylim(top=1000)
    plt.show()


if __name__ == '__main__':
    train()
    # main()
