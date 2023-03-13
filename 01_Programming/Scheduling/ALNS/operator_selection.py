import numpy as np
from Scheduling.ALNS.acceptance_criterion import Acceptance
import random as rd


class OPSelection(Acceptance):
    def __init__(self, operators):
        """
        i... index of operators
        u... the number of times the operator has been used
        beta ... score (initialized as 0)
        w_i ... the weighing of the operator
        rho ... parameter that controls how quickly the weight reacts to the operators performance 
        """
        self.lst_operators = operators
        w_initial = 1/len(operators)
        self.w_i = np.full(len(operators), w_initial)
        self.u_i = np.full(len(operators), 0)
        self.beta_i = np.full(len(operators), 0)
        self.rho = 0.5
        self.seed = 999

    def update_weighing(self):
        pass

    def select_and_apply(self):
        rd.seed(self.seed)
        random_number = rd.uniform(0, 1)
        self.seed = self.seed + 1
        operator = self.select_operator_acc_rd_number(random_number)
        return operator

    def select_operator_acc_rd_number(self, random_number):
        last_accumulative_weighing = 0
        for i in range(len(self.w_i)):
            new_accumulative_weighing = last_accumulative_weighing+self.w_i[i]
            if last_accumulative_weighing < random_number < new_accumulative_weighing:
                break
            else:
                last_accumulative_weighing = new_accumulative_weighing

        return self.operator[i]

