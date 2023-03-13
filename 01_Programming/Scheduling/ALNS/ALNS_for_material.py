from destroy_operator import Destroy
from repair_operator import Repair
from acceptance_criterion import Acceptance
from Scheduling.ALNS.solve_permutation import SolvePermutation
import random as rd


class ALNS_material(Destroy, Repair, Acceptance):
    def __init__(self, input_dfs):
        self.plan_permutation = SolvePermutation(input_dfs)
        self.removed_parts_p = []
        self.pi = []
        Destroy.__init__(self, self.plan_permutation, self.pi, self.removed_parts_p)
        Repair.__init__(self, self.plan_permutation, self.pi, self.removed_parts_p)
        self.pi_prime = None
        self.pi_best = None
        self.obj_values = []
        self.number_of_max_iterations = 400
        self.number_of_iterations = 0
        self.seed = 999

    def increment_number_of_iterations(self):
        self.number_of_iterations += 1

    def solve(self):
        """
        phi is the objective value of the current solution
        """
        self.create_inital_solution()
        termination_criterion = False
        while not termination_criterion:
            self.increment_number_of_iterations()
            destroy_operator = self.destroy()
            repair_operator = self.repair()
            phi = repair_operator.self.obj_value
            accepted, theta = self.check_acceptance(phi)
            destroy_operator.update_weight(theta)
            repair_operator.update_weight(theta)
            if accepted:
                self.pi_prime = self.pi.copy()
                self.obj_values.append(phi)
                if phi < min(self.obj_values):
                    self.pi_best = self.pi.copy()

            termination_criterion = self.check_termination_criterion()

    def check_termination_criterion(self):
        if self.number_of_iterations >= self.number_of_max_iterations:
            return True

    def create_inital_solution(self):
        rd.seed(self.seed)
        pi = list(self.plan_permutation.params.P).copy()
        rd.shuffle(self.vars.pi)
        self.seed += 1
        self.plan_permutation(pi)



