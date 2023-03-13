import numpy as np
import random


class OPSelection:
    def __init__(self, operators):
        """
        i... index of operators
        u... the number of times the operator has been used
        beta ... score (initialized as 0)
        w_i ... the weighing of the operator
        rho ... parameter that controls how quickly the weight reacts to the operators performance 
        """
        self.lst_operators = operators
        w_i = 1/len(operators)
        self.weighing = np.full(len(operators), w_i)
        self.u_i = np.full(len(operators), 0)
        self.beta_i = np.full(len(operators), 0)
        self.rho = 0.5
        beta_lower = 0.0
        beta_higher = 0.0
        beta_accept = 0.0

    def update_weighing(self):
        pass

    def select_and_apply(self):


        pass

    def add_objective_value(self):
