import pandas as pd

class VariablesALNS:
    def __init__(self):
        self.F_jp = {}
        self.b_j = {}
        self.e_j = {}
        self.T_j = {}
        self.U_j = {}
        self.Y_jj = {}

        self.x_p = {}
        self.y_p = {}
        self.n_j = {}
        self.z_p = {}
        self.J = []
        self.P_j = {}

        self.df_O = pd.DataFrame()
        self.pi = []
        self.permutations_used = {}