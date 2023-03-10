from fast_pack import FastPack
from scheduling import Scheduling
from costs import Costs
from model import ModelMachineALNS

class SolvePermutation(ModelMachineALNS, FastPack, Scheduling, Costs):
    def __init__(self, params, pi):
        ModelMachineALNS.__init__(self, params)
        self.pi = pi

    def solve_permutation(self):
        self.fast_packing()
        self.schedule()
        self.compute_costs()

