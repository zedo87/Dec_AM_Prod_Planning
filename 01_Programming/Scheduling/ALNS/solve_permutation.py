from fast_pack import FastPack
from scheduling import Scheduling
from Scheduling.costs import CostsMachine
from model import ModelMachineALNS

class SolvePermutation(FastPack, Scheduling, CostsMachine):
    def __init__(self, input_dfs):
        self.model = ModelMachineALNS(input_dfs)
        self.solver_successful = True

    def solve_permutation(self, pi):
        self.fast_packing(pi)
        self.schedule()
        self.post_processing_costs()

