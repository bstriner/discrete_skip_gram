import keras.backend as K
import numpy as np
import theano.tensor as T


def normal_initializer(scale):
    return lambda size: np.random.uniform(low=-scale, high=scale, size=size)


class MLP(object):
    def __init__(self,
                 input_units,
                 hidden_units,
                 output_units,
                 hidden_depth,
                 initializer=normal_initializer(0.05),
                 hidden_activation=None,
                 output_activation=None):
        self.hidden_depth = hidden_depth
        self.hidden_activation = hidden_activation
        self.output_activation = output_activation
        self.params = []
        self.params.append(K.variable(initializer((input_units, hidden_units))))
        self.params.append(K.variable(initializer((hidden_units,))))
        for i in range(hidden_depth):
            self.params.append(K.variable(initializer((hidden_units, hidden_units))))
            self.params.append(K.variable(initializer((hidden_units,))))
        self.params.append(K.variable(initializer((hidden_units, output_units))))
        self.params.append(K.variable(initializer((output_units,))))

    def call(self, x):
        return self.call_on_params(x, self.params)

    def call_on_params(self, x, params):
        assert len(params) == (2 * self.hidden_depth) + 4
        h = T.dot(x, params[0]) + params[1]
        if self.hidden_activation:
            h = self.hidden_activation(h)
        for j in range(self.hidden_depth):
            h = T.dot(h, params[2 + (2 * j)]) + params[3 + (2 * j)]
            if self.hidden_activation:
                h = self.hidden_activation(h)
        y = T.dot(h, params[-2]) + params[-1]
        if self.output_activation:
            y = self.output_activation(y)
        return y
