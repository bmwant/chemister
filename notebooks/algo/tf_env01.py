import os
import abc
import argparse

import tensorflow as tf
import tensorflow.contrib.eager as tfe
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from absl import app, logging
from tf_agents.agents.dqn import q_network, dqn_agent
from tf_agents.networks import q_rnn_network
from tf_agents.drivers import dynamic_episode_driver
from tf_agents.environments import (
    trajectory,
    py_environment,
    tf_environment,
    tf_py_environment,
    wrappers,
    suite_gym,
    utils,
)
from tf_agents.environments import time_step as ts
from tf_agents.policies import (
    random_tf_policy,
    greedy_policy,
    epsilon_greedy_policy,
    tf_py_policy,
)
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.metrics import metric_utils, tf_metrics
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
tf.enable_eager_execution()
FLAGS = None
VERBOSE = False
MAX_AMOUNT = 1000


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



def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log_dir',
        type=str,
        default='/tmp/tensorflow/logs/tfenv',
        help='summaries log directory',
    )
    FLAGS, unparsed = parser.parse_known_args()
    if tf.gfile.Exists(FLAGS.log_dir):
        tf.gfile.DeleteRecursively(FLAGS.log_dir)
    tf.gfile.MakeDirs(FLAGS.log_dir)
    train()


def train():
    summary_interval = 1000
    summaries_flush_secs = 10
    num_eval_episodes = 5
    root_dir = '/tmp/tensorflow/logs/tfenv01'
    train_dir = os.path.join(root_dir, 'train')
    eval_dir = os.path.join(root_dir, 'eval')
    train_summary_writer = tf.compat.v2.summary.create_file_writer(
        train_dir, flush_millis=summaries_flush_secs*1000)
    train_summary_writer.set_as_default()
    eval_summary_writer = tf.compat.v2.summary.create_file_writer(
        eval_dir, flush_millis=summaries_flush_secs*1000)
    # maybe py_metrics?
    eval_metrics = [
        tf_metrics.AverageReturnMetric(buffer_size=num_eval_episodes),
        tf_metrics.AverageEpisodeLengthMetric(buffer_size=num_eval_episodes),
    ]

    environment = TradeEnvironment()
    # utils.validate_py_environment(environment, episodes=5)
    # Environments
    global_step = tf.compat.v1.train.get_or_create_global_step()
    with tf.compat.v2.summary.record_if(
            lambda: tf.math.equal(global_step % summary_interval, 0)):
        train_env = tf_py_environment.TFPyEnvironment(environment)
        eval_env = tf_py_environment.TFPyEnvironment(environment)

        num_iterations = 50
        fc_layer_params = (512, )  # ~ (17 + 1001) / 2
        input_fc_layer_params = (50, )
        output_fc_layer_params = (20, )
        lstm_size = (30, )
        
        initial_collect_steps = 20
        collect_steps_per_iteration = 1
        collect_episodes_per_iteration = 1  # the same as above
        batch_size = 64
        replay_buffer_capacity = 10000
        
        train_sequence_length = 10

        gamma = 0.99  # check if 1.0 works as well
        target_update_tau = 0.05
        target_update_period = 5
        epsilon_greedy = 0.1
        gradient_clipping = None
        reward_scale_factor = 1.0

        learning_rate = 1e-2
        log_interval = 30
        eval_interval = 15

        # train_env.observation_spec(),
        q_net = q_rnn_network.QRnnNetwork(
            train_env.time_step_spec().observation,
            train_env.action_spec(),
            input_fc_layer_params=input_fc_layer_params,
            lstm_size=lstm_size,
            output_fc_layer_params=output_fc_layer_params,
        )

        optimizer = tf.compat.v1.train.AdamOptimizer(
            learning_rate=learning_rate)

        tf_agent = dqn_agent.DqnAgent(
            train_env.time_step_spec(),
            train_env.action_spec(),
            q_network=q_net,
            optimizer=optimizer,
            epsilon_greedy=epsilon_greedy,
            target_update_tau=target_update_tau,
            target_update_period=target_update_period,
            td_errors_loss_fn=dqn_agent.element_wise_squared_loss,
            gamma=gamma,
            reward_scale_factor=reward_scale_factor,
            gradient_clipping=gradient_clipping,
            debug_summaries=False,
            summarize_grads_and_vars=False,
            train_step_counter=global_step,
        )

        replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
            tf_agent.collect_data_spec,
            batch_size=train_env.batch_size,
            max_length=replay_buffer_capacity,
        )

        train_metrics = [
            tf_metrics.NumberOfEpisodes(),
            tf_metrics.EnvironmentSteps(),
            tf_metrics.AverageReturnMetric(),
            tf_metrics.AverageEpisodeLengthMetric(),
        ]

        # Policy which does not allow some actions in certain states
        q_policy = FilteredQPolicy(
            tf_agent._time_step_spec, 
            tf_agent._action_spec, 
            q_network=tf_agent._q_network,
        )

        # Valid policy to pre-fill replay buffer
        initial_collect_policy = DummyTradePolicy(
            train_env.time_step_spec(),
            train_env.action_spec(),
        )
        print('Initial collecting...')
        initial_collect_op = dynamic_episode_driver.DynamicEpisodeDriver(
            train_env,
            initial_collect_policy,
            observers=[replay_buffer.add_batch] + train_metrics,
            num_episodes=initial_collect_steps,
        ).run()

        # Main agent's policy; greedy one
        policy = greedy_policy.GreedyPolicy(q_policy)
        # Policy used for evaluation, the same as above
        eval_policy = greedy_policy.GreedyPolicy(q_policy)
    
        tf_agent._policy = policy
        collect_policy = epsilon_greedy_policy.EpsilonGreedyPolicy(
            q_policy, epsilon=tf_agent._epsilon_greedy)
        # Patch random policy for epsilon greedy collect policy
        filtered_random_tf_policy = FilteredRandomTFPolicy(
            time_step_spec=policy.time_step_spec,
            action_spec=policy.action_spec,
        )
        collect_policy._random_policy = filtered_random_tf_policy
        tf_agent._collect_policy = collect_policy
        collect_op = dynamic_episode_driver.DynamicEpisodeDriver(
            train_env,
            collect_policy,
            observers=[replay_buffer.add_batch] + train_metrics,
            num_episodes=collect_episodes_per_iteration,
        ).run()
        dataset = replay_buffer.as_dataset(
            num_parallel_calls=3,
            sample_batch_size=batch_size,
            num_steps=train_sequence_length+1,
        ).prefetch(3)

        iterator = iter(dataset) 
        experience, _ = next(iterator)
        loss_info = common.function(tf_agent.train)(experience=experience)

        # Checkpoints
        train_checkpointer = common.Checkpointer(
            ckpt_dir=train_dir,
            agent=tf_agent,
            global_step=global_step,
            metrics=metric_utils.MetricsGroup(train_metrics, 'train_metrics'),
        )
        policy_checkpointer = common.Checkpointer(
            ckpt_dir=os.path.join(train_dir, 'policy'),
            policy=tf_agent.policy,
            global_step=global_step,
        )
        rb_checkpointer = common.Checkpointer(
            ckpt_dir=os.path.join(train_dir, 'replay_buffer'),
            max_to_keep=1,
            replay_buffer=replay_buffer,
        )
        
        summary_ops = []
        for train_metric in train_metrics:
            summary_ops.append(train_metric.tf_summaries(
                train_step=global_step,
                step_metrics=train_metrics[:2],
            ))

        with eval_summary_writer.as_default(), \
                tf.compat.v2.summary.record_if(True):
            for eval_metric in eval_metrics:
                eval_metric.tf_summaries(train_step=global_step)

        init_agent_op = tf_agent.initialize()
    
        with tf.compat.v1.Session() as sess:
            # sess.run(train_summary_writer.init())
            # sess.run(eval_summary_writer.init())
            
            # Initialize the graph
            # tfe.Saver().restore()
            # train_checkpointer.initialize_or_restore()
            # rb_checkpointer.initialize_or_restore()
            # sess.run(iterator.initializer)
            common.initialize_uninitialized_variables(sess)

            sess.run(init_agent_op)
            print('Collecting initial experience...')
            sess.run(initial_collect_op)

            global_step_val = sess.run(global_step)
            metric_utils.compute_summaries(
                eval_metrics,
                eval_env,
                eval_policy,
                num_episodes=num_eval_episodes,
                global_step=global_step_val,
                callback=eval_metrics_callback,
                log=True,
            )

            collect_call = sess.make_callable(collect_op)
            train_step_call = sess.make_callable([loss_info, summary_ops])
            global_step_call = sess.make_callable(global_step)

            timed_at_step = global_step_call()
            time_acc = 0
            steps_per_second_ph = tf.compat.v1.placeholder(
                tf.float32, shape=(), name='steps_per_sec_ph')
            steps_per_second_summary = tf.compat.v2.summary.scalar(
                name='global_steps_per_sec',
                data=steps_per_second_ph,
                step=global_step,
            )

            # Train
            for i in range(num_iterations):
                start_time = time.time()
                collect_call()

                for _ in range(train_steps_per_iteration):
                    loss_info_value, _ = train_step_call()
                time_acc += time.time() - start_time
                global_step_val = global_step_call()

                if global_step_val % log_inerval == 0:
                    print('step=%d, loss=%f', 



                          global_step_val, loss_info_value.loss)
                    steps_per_sec = (global_step_val-timed_at_step) / time_acc
                    print('%.3f steps/sec', steps_per_sec)
                    sess.run(
                        steps_per_second_summary,
                        feed_dict={steps_per_second_ph: steps_per_sec},
                    )
                    timed_at_step = global_step_val
                    time_acc = 0

                # Save checkpoints
                if global_step_val % train_checkpoint_interval == 0:
                    train_checkpointer.save(global_step=global_step_val)

                if global_step_val % policy_checkpoint_interval == 0:
                    policy_checkpointer.save(global_step=global_step_val)

                if global_step_val % rb_checkpoint_interval == 0:
                    rb_checkpointer.save(global_step=global_step_val)

                # Evaluate
                if global_step_val % eval_interval == 0:
                    metric_utils.compute_summaries(
                        eval_metrics,
                        eval_env,
                        eval_policy,
                        num_episodes=num_eval_episodes,
                        global_step=global_step_val,
                        log=True,
                        callback=eval_metrics_callback,
                    )
    print('Done!')        


def main(_):
    logging.set_verbosity(logging.INFO)
    tf.enable_resource_variables()
    train()
    

if __name__ == '__main__':
    app.run(main)
    # main()
