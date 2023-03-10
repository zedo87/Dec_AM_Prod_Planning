import gurobipy as gp
from gurobipy import GRB


class ObjectiveFunctionMachine:
    def __init__(self):
        self.vars = None
        self.params = None
        self.grb = None

    def build_objective_function(self):
        self.grb.setObjective(gp.quicksum(self.params.tau * self.vars.e_j[j] for j in self.params.J)
                           + gp.quicksum(self.params.rho_hour * self.params.v_p[p] * self.params.t_p[p]
                                         for p in self.params.P)
                           - gp.quicksum(self.params.rho_hour * self.params.v_p[p] * self.vars.z_p[p]
                                         for p in self.params.P)

                           + gp.quicksum(self.params.sigma * self.params.s_m * self.params.S_jj.get((j, j_prime), 0)
                                         * self.vars.Y_jj[(j, j_prime)]
                                         for j in self.params.J for j_prime in self.params.J_star)

                           + gp.quicksum(self.params.sigma * self.params.s_b * self.vars.Y_jj[(j, j_prime)]
                                         for j in self.params.J for j_prime in self.params.J_star)

                           + gp.quicksum(self.params.chi_p[p] for p in self.params.P), GRB.MINIMIZE)


class ObjectiveFunctionSite:
    def __init__(self):
        self.vars = None
        self.params = None
        self.grb = None

    def build_objective_function(self):
        self.grb.setObjective(gp.quicksum(self.params.tau * self.vars.e_j[j] for j in self.params.J)
                           + gp.quicksum(self.params.sigma * self.params.s_m *
                                         self.vars.Y_ijj[(i, j, j_prime)] * self.params.S_jj.get((j, j_prime), 0)
                                         for j in self.params.J for j_prime in self.params.J_star for i in self.params.I)

                           + gp.quicksum(self.params.sigma * self.params.s_b * self.vars.Y_ijj[(i, j, j_prime)]
                                         for j in self.params.J for j_prime in self.params.J_star for i in self.params.I)

                           + gp.quicksum(self.params.chi_p[p] for p in self.params.P)
                           + gp.quicksum(self.params.rho_hour * self.params.v_p[p] *
                                         self.params.t_p[p] for p in self.params.P)
                           - gp.quicksum(self.params.rho_hour * self.params.v_p[p] *
                                         self.vars.z_p[p] for p in self.params.P), GRB.MINIMIZE)

class ObjectiveFunctionMultiSite:
    def __init__(self):
        self.vars = None
        self.params = None
        self.grb = None

    def build_objective_function(self):
        self.grb.setObjective(gp.quicksum(self.params.tau * self.vars.e_j[j] for j in self.params.J)

                           + gp.quicksum(self.params.sigma * self.params.s_m *
                                         self.vars.Y_ijj[(i, j, j_prime)] * self.params.S_jj.get((j, j_prime), 0)
                                         for j in self.params.J for j_prime in self.params.J_star for i in self.params.I)

                           + gp.quicksum(self.params.sigma * self.params.s_b * self.vars.Y_ijj[(i, j, j_prime)]
                                         for j in self.params.J for j_prime in self.params.J_star for i in self.params.I)

                           + gp.quicksum(self.params.chi_jp[(j, p)] * self.vars.F_jp[(j, p)]
                                         for j in self.params.J for p in self.params.P)

                           + gp.quicksum(self.params.rho_hour * self.params.v_p[p] *
                                         self.params.t_p[p] for p in self.params.P)
                           - gp.quicksum(self.params.rho_hour * self.params.v_p[p] *
                                         self.vars.z_p[p] for p in self.params.P), GRB.MINIMIZE)