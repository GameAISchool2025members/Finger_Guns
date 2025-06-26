import copy
import math


class NN:
    def __init__(self, weights, activation_function = math.tanh):
        self.weights = copy.deepcopy(weights)
        self.act_func = activation_function

    def compute(self, values):
        prev_vals = values
        for layer in self.weights:
            next_vals = []
            for neuron in layer:
                counter = 0.0
                for i in range(len(neuron) - 1):
                    counter += neuron[i] * prev_vals[i]
                counter += neuron[len(neuron) - 1]
                next_vals.append(self.act_func(counter))
            prev_vals = next_vals
        return prev_vals
