from math import inf
from math import exp
import random as rd

class Acceptance:
    def __init__(self):
        """
        acceptance criterion for the ALNS, acceptance criterion is based on metropolis criterion, which is also used
        in simulated annealing.
        T is the cooling temperatur
        alpha is the cooling rate
        k is the reaction coefficient
        initial values obtained from Zeng. et al 2021 (Table 1).
          """
        self.theta_1 = 2
        self.theta_2 = 1.3
        self.theta_3 = 1
        self.T = 0.2
        self.alpha = 0.95
        self.k = 0.6
        self.max_iterations = 400
        self.objective_values = []
        self.seed = 999
    def check_acceptance(self, objective_value):
        """
        case 1: if new objective value is lower than the best one, accept and use theta 1
        case 2: if new objective value is lower than the last one, accept and use theta 2
        case 3: if new objective value is higher than last one use metropolos criterion. if this accepts, use theta 3
        """

        theta = 0

        if objective_value < min(self.objective_values):
            accept = True
            theta = self.theta_1
        elif objective_value < self.objective_values[-1]:
            accept = True
            theta = self.theta_2
        else:
            accept = self.check_metropolis_criterion(objective_value)
            if accept:
                theta = self.theta_3

        if accept: self.objective_values.append(objective_value)

        self.update_T()
        return accept, theta

    def check_metropolis_criterion(self, objective_value):
        probability = exp((self.objective_values[-1] - objective_value)/self.T)
        rd.seed(self.seed)
        random_number = rd.uniform(0, 1)
        self.seed += self.seed
        acceptance = False
        if random_number < probability:
            acceptance = True
        return acceptance

    def update_T(self):
        self.T = self.alpha * self.T







