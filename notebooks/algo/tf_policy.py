import numpy as np
import tensorflow as tf
import tensorflow.contrib.eager as tfe
import tensorflow_probability as tfp
from tensorflow.python.framework import ops
from tf_agents.policies import policy_step
from tf_agents.policies import tf_policy
from tf_agents.policies.q_policy import QPolicy
from tf_agents.policies.random_tf_policy import RandomTFPolicy
from tf_agents.policies.random_py_policy import RandomPyPolicy
from tf_agents.specs import array_spec, tensor_spec
from tf_agents.utils import nest_utils


class DummyTradePolicy(tf_policy.Base):

    def _variables(self):
        return []

    def _action(self, time_step, policy_state, seed):
        step = time_step.observation.numpy()[0][-1]
        if step < 15:
            a_ = np.random.randint(0, 66)
        else:
            days_left = np.max([30 - step, 1])
            can_sale = time_step.observation.numpy()[0][-3]
            can_sale_daily = can_sale / days_left
            a_ = -np.random.randint(0, can_sale_daily+1)

        a_ += 500  # add shift to start with 0
        # print('Observation', time_step.observation.numpy())
        # print('Step', step, 'Action:', a_, 'Action value', a_-500)

        action_ = ops.convert_to_tensor(np.array([a_], dtype=np.int32))
        if time_step is not None:
            with tf.control_dependencies(tf.nest.flatten(time_step)):
                action_ = tf.nest.map_structure(tf.identity, action_)

        return policy_step.PolicyStep(action_, policy_state)

    def _distribution(self, time_step, policy_state):
        raise NotImplementedError(
            'DummyTradePolicy does not support distributions'
        )


class FilteredRandomTFPolicy(RandomTFPolicy):
    def _action(self, time_step, policy_state, seed):
        outer_dims = nest_utils.get_outer_shape(
            time_step, self._time_step_spec)

        observation = time_step.observation.numpy()[0]
        amount_now = observation[-3]  # can sale
        amount_available = observation[-2]  # can buy
        lower_bound = int(500 - amount_now)
        upper_bound = int(amount_available + 1)
        actions_available = np.arange(lower_bound, upper_bound)
        a_ = np.random.choice(actions_available)
        action_ = ops.convert_to_tensor(np.array([a_], dtype=np.int32))
        
        if time_step is not None:
            with tf.control_dependencies(tf.nest.flatten(time_step)):
                action_ = tf.nest.map_structure(tf.identity, action_)

        return policy_step.PolicyStep(action_, policy_state)


class FilteredQPolicy(QPolicy):
    def _distribution(self, time_step, policy_state):
        q_values, policy_state = self._q_network(
            time_step.observation, time_step.step_type, policy_state,
        )
        q_values.shape.assert_has_rank(2)


        if self._action_shape.ndims == 1:
            q_values = tf.expand_dims(q_values, -2)

        observation = time_step.observation.numpy()[0]
        amount_now = observation[-3]  # can sale
        amount_available = observation[-2]  # can buy
        q_values_np = q_values.numpy()[0]
        lower_bound = int(500 - amount_now)
        upper_bound = int(amount_available + 1)
        q_values_np[:lower_bound] = -np.inf
        q_values_np[upper_bound:] = -np.inf

        new_q_values = ops.convert_to_tensor(
            np.array([q_values_np], dtype=np.float32))

        distribution = tfp.distributions.Categorical(
            logits=new_q_values, dtype=self._action_dtype
        )
        distribution = tf.nest.pack_sequence_as(
            self._action_spec, [distribution]
        )
        return policy_step.PolicyStep(distribution, policy_state)
    

class FilteredRandomPyPolicy(RandomPyPolicy):
    def _action(self, time_step, policy_state):
        outer_dims = self._outer_dims
        if outer_dims is None:
            if self.time_step_spec.observation:
                outer_dims = nest_utils.get_outer_array_shape(
                    time_step.observation,
                    self.time_step_spec.observation,
                )
            else:
                outer_dims = ()
        random_action = array_spec.sample_spec_nest(
            self._action_spec,
            self._rng,
            outer_dims=outer_dims,
        )
        print('Action rnd', random_action)
        return policy_step.PolicyStep(random_action, policy_state)
