from model import ModelMachineALNS

class ALNS_Algorithm(ModelMachineALNS):
    """
    This is an ALNS algorithm for the single-site batching scheduling problem. It is inspired by
    Zeng, J. and Zhang, X. (2021) ‘An Adaptive Large Neighborhood Search for Single-Machine Batch Processing
    Scheduling With 2-D Rectangular Bin-Packing Constraints’, IEEE Transactions on Reliability. I
    EEE, pp. 1–10. doi: 10.1109/TR.2021.3128167.
    It is adapted to the objective function of the model of:

    Zehetner, D. and Gansterer, M. (2022) ‘The collaborative batching problem in multi-site additive manufacturing’,
    International Journal of Production Economics, p. 108432. doi: 10.1016/j.ijpe.2022.108432.
    """
    def __int__(self):
        """
        removed_parts is the part list which is filled by destroy operators, the repair operator inserts the part in
        the permutation pi,
        number_of_parts_to_remove is a random number which defines the number of destroy operations
        T is the cooling temperature
        :return:
        """
        self.seed = 999
        self.removed_parts_p = []
        self.number_of_parts_to_remove = 0

        self.pi = []

    def __init__(self, params):
        ModelMachineALNS.__init__(self, params)

    def solve_model(self, seed):
        self.vars.pi = self.create_permutation_of_parts(seed)



    def solve_material(self):
        pass


    def merge_material_plans(self):
        pass














