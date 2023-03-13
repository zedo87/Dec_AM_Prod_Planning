import random as rd
from operator_selection import OPSelection

class Destroy:
    def __init__(self):
        self.destroy_operator_selection = OPSelection([self.random_removal, self.worst_removal])
        self.removed_parts_p = None
        self.pi = None

    def random_removal(self, number_of_items_to_delete):
        for i in range(number_of_items_to_delete):
            self.removed_parts_p.append(self.pi.pop(rd.randrange(len(self.pi))))

    def worst_removal(self, number_of_items_to_delete):
        for i in range(number_of_items_to_delete):
            pass

    def destroy(self):
        number_of_items_to_delete = 0
        operator = self.destroy_operator_selection.select_operator_acc_rd_number()
        operator(number_of_items_to_delete)
