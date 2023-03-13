import numpy as np
from Scheduling.ALNS.acceptance_criterion import Acceptance
import random as rd

class OperatorWeighing:
    def __init__(self):
        """W
        w weighing of operator
        u number operator used
        beta parameter for theta
        rho parameter that controls weight adjustmens
        """
        self.w = 1.0
        self.u = 0
        self.beta = 0.0
        self.rho = 0.5

    def increment_operator_counter(self):
        self.u += 1

    def determine_weighing(self):
        self.w = (1-self.rho)*self.w + self.rho * self.beta / self.u

    def update_weight(self, theta):
        self.beta += theta
        self.increment_operator_counter()
        self.determine_weighing()

class OPSelection:
    def __init__(self, operators):
        self.lst_operators = operators
        self.sum_weights = 0

        self.seed = 999

    def set_sum_weights(self):
        self.sum_weights = 0
        for operator in self.lst_operators:
            self.sum_weights += operator.w

    def select_and_apply(self):
        rd.seed(self.seed)
        random_number = rd.uniform(0, self.sum_weights)
        self.seed = self.seed + 1
        operator = self.select_operator_acc_rd_number(random_number)
        return operator

    def select_operator_acc_rd_number(self, random_number):
        last_accumulative_weighing = 0
        i = 0
        for i in range(len(self.lst_operators)):
            new_accumulative_weighing = last_accumulative_weighing+ self.lst_operators[i].w
            if last_accumulative_weighing < random_number < new_accumulative_weighing:
                break
            else:
                last_accumulative_weighing = new_accumulative_weighing
        return self.lst_operators[i]

