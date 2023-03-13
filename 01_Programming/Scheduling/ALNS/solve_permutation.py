from fast_pack import FastPack
from scheduling import Scheduling
from Scheduling.costs import CostsMachine
from model import ModelMachineALNS

class SolvePermutation(ModelMachineALNS, FastPack, Scheduling, CostsMachine):
    def __init__(self, input_dfs):
        ModelMachineALNS.__init__(self, input_dfs)
        self.pi = None

    def solve_permutation(self, pi):
        self.fast_packing(pi)
        self.schedule()
        self.post_processing_costs()

