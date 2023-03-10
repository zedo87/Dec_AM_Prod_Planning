import random as rd
from operator_selection import OPSelection

class Destroy(OPSelection):
    def __init__(self):
        self.removed_parts_p = None
        self.pi = None

    def random_removal(self, number_of_items_to_delete):
        for i in range(number_of_items_to_delete):
            self.removed_parts_p.append(self.pi.pop(rd.randrange(len(self.pi))))

    def worst_removal(self, number_of_items_to_delete):
        for i in range(number_of_items_to_delete):
            pass


