from destroy_operator import Destroy
from repair_operator import Repair
from operator_selection import OPSelection
from acceptance_criterion import Acceptance

class ALNS_material(Destroy, Repair, Acceptance):
    def __init__(self):


        destroy_operators = OPSelection()
        repair_operators = OPSelection()

        self.removed_parts_p = None
        self.pi = None
        
        self.obj_values = []

    def solve(self):
        self.create_inital_solution()
        acceptance_criterion = False
        while not acceptance_criterion:
            self.destroy()
            self.repair()
            self.fast_pack_solve
            acceptance_criterion = self.acceptance_criterion_fulfilled()


    def check_termination_criterion(self):



    def create_inital_solution(self):


