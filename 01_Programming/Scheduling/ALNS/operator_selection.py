import numpy as np
import random

class Operator:
    def __init__(self, method):
        C_i = 0
        w_i =
        method = method



class OPSelection:
    def __init__(self, operators):
        """
        :param operators: a list of methods of operators
        :return:
        """
        initial_weighing = 1/len(operators)
        self.weighing = np.full(len(operators), initial_weighing)
        self.lst_operators = operators

    def update_weighing(self):
        pass

    def select_and_apply(self):


        pass