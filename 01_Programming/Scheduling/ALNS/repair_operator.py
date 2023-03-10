from operator_selection import OPSelection
import random as rd

class Repair(OPSelection):
    def __init__(self):
        OPSelection.__init__([self.random_insertion, self.greedy_insertion])
        self.removed_parts_p = None
        self.pi = None
        self.seed = None

    def random_insertion(self):
        while len(self.removed_parts_p) > 0:
            p = self.removed_parts_p.pop()
            rd.seed(self.seed)
            index_to_insert = rd.randint(0, len(self.pi))
            self.pi.insert(p, index_to_insert)
            self.seed += 1

    def greedy_insertion(self):
        pass

    def repair(self):



