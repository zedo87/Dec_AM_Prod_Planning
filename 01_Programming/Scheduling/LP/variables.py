import gurobipy as gp
import pandas as pd
from gurobipy import GRB


class Variables:
    def __init__(self, params, grb):
        self.F_jp = grb.addVars(params.list_jp, vtype=GRB.BINARY, name="F_jp")
        self.b_j = grb.addVars(gp.tuplelist(params.J), lb=0, ub=max(params.h_p.values()) + 1, vtype=GRB.CONTINUOUS, name="b_j")
        self.e_j = grb.addVars(gp.tuplelist(params.J), lb=0, ub=max(params.t_p.values()), vtype=GRB.CONTINUOUS, name="e_j")
        self.T_j = grb.addVars(gp.tuplelist(params.J), lb=0, ub=max(params.t_p.values()), vtype=GRB.CONTINUOUS, name="T_j")
        self.U_j = grb.addVars(gp.tuplelist(params.J), lb=0, ub=max(params.t_p.values()), vtype=GRB.CONTINUOUS, name="U_j")

        self.x_p = grb.addVars(gp.tuplelist(params.P), lb=0, ub=params.f_pc, vtype=GRB.CONTINUOUS, name="x_p")
        self.y_p = grb.addVars(gp.tuplelist(params.P), lb=0, ub=params.f_pc, vtype=GRB.CONTINUOUS, name="y_p")
        self.z_p = grb.addVars(gp.tuplelist(params.P), lb=0, ub=max(params.t_p.values()), vtype=GRB.CONTINUOUS, name="z_p")
        self.w_pp_1 = grb.addVars(params.list_pp_tick, vtype=GRB.BINARY, name="w_pp_1")
        self.w_pp_2 = grb.addVars(params.list_pp_tick, vtype=GRB.BINARY, name="w_pp_2")
        self.w_pp_3 = grb.addVars(params.list_pp_tick, vtype=GRB.BINARY, name="w_pp_3")
        self.w_pp_4 = grb.addVars(params.list_pp_tick, vtype=GRB.BINARY, name="w_pp_4")


class VariablesMachine(Variables):
    def __init__(self, params, grb):
        Variables.__init__(self, params, grb)
        self.Y_jj = grb.addVars(params.list_jj_tick, vtype=GRB.BINARY, name="Y_jj")


class VariablesSite:
    def __init__(self, params, grb):
        Variables.__init__(self, params, grb)
        self.Y_ijj = grb.addVars(params.list_ijj_tick, vtype=GRB.BINARY, name="Y_ijj")





