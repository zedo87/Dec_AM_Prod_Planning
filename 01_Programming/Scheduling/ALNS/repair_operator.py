from math import inf


from operator_selection import OPSelection, OperatorWeighing
import random as rd
from Scheduling.ALNS.fast_pack import FastPack

class Repair:
    def __init__(self, plan_permutation, pi, removed_parts_p):
        self.repair_operator_selection = OPSelection([GreedyInsertion(plan_permutation, pi, removed_parts_p),
                                                      RandomInsertion(plan_permutation, pi, removed_parts_p)])
        self.removed_parts_p = None
        self.pi = None
        self.seed = None

    def repair(self):
        operator = self.repair_operator_selection.select_operator_acc_rd_number()
        operator.apply()
        return operator

class GreedyInsertion(OperatorWeighing):
    def __init__(self, plan_permutation, pi, removed_parts_p):
        OperatorWeighing.__init__(self)
        self.plan_permutation = plan_permutation
        self.obj_value = None
        self.pi = pi
        self.removed_parts_p = removed_parts_p


    def apply(self):
        while len(self.removed_parts_p) > 0:
            best_j = None
            best_obj_value = inf
            p = self.removed_parts_p.pop()
            for j in range(len(self.pi)):
                temp_pi = self.pi.copy()
                self.temp_pi.insert(p, j)
                self.plan_permutation.solve(temp_pi)
                if self.plan_permutation.total_costs < best_obj_value:
                    best_obj_value = self.plan_permutation.total_costs
                    best_j = j
            self.pi.insert(p, best_j)


class RandomInsertion(OperatorWeighing):
    def __init__(self, plan_permutation, pi, removed_parts_p):
        OperatorWeighing.__init__(self)
        self.fast_pack_inst = plan_permutation
        self.obj_value = None
        self.pi = pi
        self.removed_parts_p = removed_parts_p

    def apply(self):
        while len(self.removed_parts_p) > 0:
            p = self.removed_parts_p.pop()
            rd.seed(self.seed)
            index_to_insert = rd.randint(0, len(self.pi))
            self.pi.insert(p, index_to_insert)
            self.seed += 1
        self.fast_pack_inst.solve(self.pi)






