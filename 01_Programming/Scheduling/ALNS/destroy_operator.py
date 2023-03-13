import random as rd
import numpy as np
from math import inf
from operator_selection import OPSelection, OperatorWeighing

class Destroy:
    def __init__(self, plan_permutation, pi, removed_parts_p):
        self.destroy_operator_selection = OPSelection([WorstRemoval(plan_permutation, pi, removed_parts_p),
                                                       RandomRemoval(plan_permutation, pi, removed_parts_p)])
        self.removed_parts_p = removed_parts_p
        self.pi = pi
        self.upper_bound_parts_to_remove = np.floor(len(self.pi)/3)
        self.seed = 999

    def random_removal(self, number_of_items_to_delete):
        for i in range(number_of_items_to_delete):
            self.removed_parts_p.append(self.pi.pop(rd.randrange(len(self.pi))))

    def worst_removal(self, number_of_items_to_delete):
        for i in range(number_of_items_to_delete):
            pass

    def destroy(self):
        rd.seed(self.seed)
        number_of_items_to_delete = rd.randint(0, self.upper_bound_parts_to_remove)
        operator = self.destroy_operator_selection.select_operator_acc_rd_number()
        operator.apply(number_of_items_to_delete)
        operator = self.destroy_operator_selection.select_operator_acc_rd_number()
        return operator

class WorstRemoval(OperatorWeighing):
    def __init__(self, plan_permutation, pi, removed_parts_p):
        OperatorWeighing.__init__(self)
        self.plan_permutation = plan_permutation
        self.pi = pi
        self.removed_parts_p = removed_parts_p
        self.seed = 999

    def apply(self, number_of_items_to_delete):
        while len(self.removed_parts_p) < number_of_items_to_delete:
            best_obj_value = inf
            for j in range(len(self.pi)):
                temp_pi = self.pi.copy()
                self.temp_pi.pop(j)
                self.plan_permutation.solve(temp_pi)
                if self.plan_permutation.total_costs < best_obj_value:
                    best_obj_value = self.plan_permutation.total_costs
                    best_j = j
                self.self.removed_parts_p.append(self.pi.pop(best_j))


class RandomRemoval(OperatorWeighing):
    def __init__(self, plan_permutation, pi, removed_parts_p):
        self.plan_permutation = plan_permutation
        OperatorWeighing.__init__(self)
        self.obj_value = None
        self.pi = pi
        self.removed_parts_p = removed_parts_p
        self.seed = 999

    def apply(self, number_of_items_to_delete):
        for i in range(number_of_items_to_delete):
            index_to_delete = rd.randint(0, len(self.pi))
            self.removed_parts_p.append(self.pi.pop(index_to_delete))
            self.seed += 1

