import gurobipy as gp
from gurobipy import GRB


class Constraints:
    def __init__(self):
        self.vars = None
        self.params = None
        self.grb = None

    def build_part_in_print_bed_x(self):
        self.grb.addConstrs(self.vars.x_p[p] + self.params.f_p[p] <= self.params.f_pc for p in self.params.P)

    def build_part_in_print_bed_y(self):
        self.grb.addConstrs(self.vars.y_p[p] + self.params.g_p[p] <= self.params.g_pc for p in self.params.P)

    def build_collision_detection(self):
        self.grb.addConstrs(self.vars.x_p[p] + self.params.f_p[p]
               <= self.vars.x_p[p_prime] + self.params.q * (3 - self.vars.F_jp[(j, p)] - self.vars.F_jp[(j, p_prime)]
                - self.vars.w_pp_1[(p, p_prime)])
                  for p in self.params.P for p_prime in self.params.P for j in self.params.J if p != p_prime)

        self.grb.addConstrs(self.vars.x_p[p_prime] + self.params.f_p[p_prime]
                <= self.vars.x_p[p] + self.params.q * (3 - self.vars.F_jp[(j, p)] - self.vars.F_jp[(j, p_prime)]
                 - self.vars.w_pp_2[(p, p_prime)])
                   for p in self.params.P for p_prime in self.params.P for j in self.params.J if p != p_prime)

        self.grb.addConstrs(self.vars.y_p[p] + self.params.g_p[p]
                <= self.vars.y_p[p_prime] + self.params.q * (3 - self.vars.F_jp[(j, p)] - self.vars.F_jp[(j, p_prime)]
                 - self.vars.w_pp_3[(p, p_prime)])
                   for p in self.params.P for p_prime in self.params.P for j in self.params.J if p != p_prime)

        self.grb.addConstrs(self.vars.y_p[p_prime] + self.params.g_p[p_prime]
                <= self.vars.y_p[p] + self.params.q * (3 - self.vars.F_jp[(j, p)] - self.vars.F_jp[(j, p_prime)]
                 - self.vars.w_pp_4[(p, p_prime)])
                   for p in self.params.P for p_prime in self.params.P for j in self.params.J if p != p_prime)

        self.grb.addConstrs(self.vars.w_pp_1[(p, p_prime)] + self.vars.w_pp_2[(p, p_prime)]
                            + self.vars.w_pp_3[(p, p_prime)] + self.vars.w_pp_4[(p, p_prime)]
                            >= 1 for p in self.params.P for p_prime in self.params.P if (p, p_prime)
                              in self.params.pp_list_material)

        self.grb.addConstr(gp.quicksum(self.vars.w_pp_1[(p, p)] + self.vars.w_pp_2[(p, p)] + self.vars.w_pp_3[(p, p)]
                                      + self.vars.w_pp_4[(p, p)] for p in self.params.P) <= 0)

    def build_speed_up_collision(self):
        self.grb.addConstrs(self.vars.w_pp_1[(p, p_prime)] + self.vars.w_pp_2[(p, p_prime)] <= 1
                              for p in self.params.P for p_prime in self.params.P if p != p_prime)

        self.grb.addConstrs(self.vars.w_pp_3[(p, p_prime)] + self.vars.w_pp_4[(p, p_prime)] <= 1
                              for p in self.params.P for p_prime in self.params.P if p != p_prime)

        self.grb.addConstrs(self.vars.w_pp_1[(p, p)] <= 0 for p in self.params.P)
        self.grb.addConstrs(self.vars.w_pp_2[(p, p)] <= 0 for p in self.params.P)
        self.grb.addConstrs(self.vars.w_pp_3[(p, p)] <= 0 for p in self.params.P)
        self.grb.addConstrs(self.vars.w_pp_4[(p, p)] <= 0 for p in self.params.P)

        self.grb.addConstr(gp.quicksum(self.vars.w_pp_1[(p, p)] + self.vars.w_pp_2[(p, p)] + self.vars.w_pp_3[(p, p)]
                                       + self.vars.w_pp_4[(p, p)] for p in self.params.P) <= 0)

    def build_all_parts_allocated(self):
        self.grb.addConstrs(gp.quicksum(self.vars.F_jp[(j, p)] for j in self.params.J) == 1 for p in self.params.P)

    def build_all_part_allocated_speed_up(self):
        self.grb.addConstr(gp.quicksum(self.vars.F_jp[(j, p)] for j in self.params.J for p in self.params.P)
                          <= self.params.number_of_parts)

    def build_batch_height(self):
        self.grb.addConstrs(self.vars.b_j[j] >= self.params.h_p[p] * self.vars.F_jp[(j, p)]
                              for j in self.params.J for p in self.params.P)

    def build_batch_duration(self):
        self.grb.addConstrs(self.vars.e_j[j] >= self.params.w_powder * self.vars.b_j[j] / self.params.r
                            + gp.quicksum(self.vars.F_jp[(j, p)] * self.params.a_p[p] * self.params.h_p[p] \
                            * self.params.w_laser / self.params.r for p in self.params.P) for j in self.params.J)

    def build_end_time_part(self):
        self.grb.addConstrs(self.vars.z_p[p]
                           <= self.vars.U_j[j] + self.vars.e_j[j]
                            + (1 - self.vars.F_jp[(j, p)]) * self.params.q for j in self.params.J for p in self.params.P)

    def build_end_time_part_speed_up(self):
        self.grb.addConstrs(self.vars.z_p[p] <= self.params.t_p[p] for p in self.params.P)

    def build_due_date_batch(self):
        self.grb.addConstrs(self.vars.T_j[j]
                          <= self.params.t_p[p] - self.params.B_p[p] - self.vars.e_j[j]
                           + self.params.q * (1 - self.vars.F_jp[(j, p)])
                             for j in self.params.J for p in self.params.P)

    def build_start_time_before_due_date(self):
        self.grb.addConstrs(self.vars.U_j[j] <= self.vars.T_j[j] for j in self.params.J)

    def build_part_to_batch_with_same_material(self):
        self.grb.addConstrs(self.params.A_mp.get((m, p), 0) * self.vars.F_jp[(j, p)] \
                 <= self.params.E_jm.get((j, m), 0) for m in self.params.M for j in self.params.J for p in self.params.P)

    def build_part_to_batch_with_same_material_speed_up(self):
        self.grb.addConstr(gp.quicksum(self.vars.F_jp[jp] for jp in self.params.jp_list_material) <= 0)


class ConstraintsMachine(Constraints):
    def __init__(self):
        self.vars = None
        self.params = None
        self.grb = None

    def build_only_part_if_batch_active(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_jj[(j, j_prime)] for j_prime in self.params.J_star)
                           >= self.vars.F_jp[(j, p)] for j in self.params.J for p in self.params.P)

    def build_only_part_if_batch_active_speed_up(self):
        self.grb.addConstr(gp.quicksum(self.vars.Y_jj[(j, j_tick)]
                                         for j_tick in self.params.J_star for j in self.params.J)
                                      <= self.params.number_of_batches)

    def build_batch_can_only_be_allocated_once(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_jj[(j, j_tick)] for j in self.params.J)
                           <= 1 for j_tick in self.params.J_star)

        self.grb.addConstrs(gp.quicksum(self.vars.Y_jj[(j, j_tick)] for j_tick in self.params.J_star)
                           <= 1 for j in self.params.J)

    def build_batch_can_only_be_allocated_once_SOS(self):
        for j_prime in self.params.J_star:
            self.grb.addSOS(GRB.SOS_TYPE1, [self.vars.Y_jj[(j, j_prime)] for j in self.params.J])

        for j in self.params.J:
            self.grb.addSOS(GRB.SOS_TYPE1, [self.vars.Y_jj[(j, j_prime)] for j_prime in self.params.J_star])

    def build_batch_can_not_be_own_successor(self):
        self.grb.addConstr(gp.quicksum(self.vars.Y_jj[(j, j)] for j in self.params.J) == 0)

    def build_batch_can_only_be_successor_if_there_is_predecessor(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_jj[(j, j_star)] for j in self.params.J)
                           <= gp.quicksum(self.vars.Y_jj[(j_star, j_prime)] for j_prime in self.params.J_star)
                              for j_star in self.params.J)

    def build_last_batch_is_zero(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_jj[(j, 0)] for j in self.params.J)
                           >= gp.quicksum(self.vars.Y_jj[(j, j_prime)] for j in self.params.J)
                              for j_prime in self.params.J)

    def build_avoid_circle_sequence(self):
        self.grb.addConstrs(self.vars.Y_jj[(j, j_prime)] + self.vars.Y_jj[(j_prime, j)] <= 1
                              for j in self.params.J for j_prime in self.params.J)


    def build_start_time_zero_if_batch_not_active(self):
        self.grb.addConstrs(self.vars.U_j[j] <= self.params.q * gp.quicksum(self.vars.Y_jj[(j, j_prime)]
                                                                              for j_prime in self.params.J_star)
                              for j in self.params.J)


    def build_start_time_batch_after_predecessor(self):
        self.grb.addConstrs(self.vars.U_j[j_prime] >=
                              self.vars.U_j[j] + self.vars.e_j[j] + self.params.s_b * self.vars.Y_jj[(j, j_prime)]
                            + self.params.s_m * self.params.S_jj.get((j, j_prime), 0) * self.vars.Y_jj[(j, j_prime)]
                            - self.params.q * (1 - self.vars.Y_jj[(j, j_prime)])
                              for j in self.params.J for j_prime in self.params.J if j != j_prime)


class ConstraintsSite(Constraints):
    def __init__(self):
        self.vars = None
        self.params = None
        self.grb = None

    def build_only_part_if_batch_active(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)]
                                 for j_prime in self.params.J_star for i in self.params.I)
                              >= self.vars.F_jp[(j, p)] for j in self.params.J for p in self.params.P)

    def build_only_part_if_batch_active_speed_up(self):
        self.grb.addConstr(gp.quicksum(self.vars.Y_ijj[(i, j, j_tick)]
                                         for j_tick in self.params.J_star for i in self.params.I for j in self.params.J)
                                        <= self.params.number_of_batches)

    def build_batch_can_only_be_allocated_once(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)] for i in self.params.I)
                             <= 1 for j in self.params.J for j_prime in self.params.J_star)

        self.grb.addConstrs(gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)] for j in self.params.J)
                           <= 1 for i in self.params.I for j_prime in self.params.J_star)

        self.grb.addConstrs(gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)] for j_prime in self.params.J_star)
                           <= 1 for i in self.params.I for j in self.params.J)

    def build_batch_can_only_be_allocated_once_SOS(self):
        for j in self.params.J:
            for j_prime in self.params.J_star:
                self.grb.addSOS(GRB.SOS_TYPE1, [self.vars.Y_ijj[(i, j, j_prime)] for i in self.params.I])

        for i in self.params.I:
            for j_prime in self.params.J_star:
                self.grb.addSOS(GRB.SOS_TYPE1, [self.vars.Y_ijj[(i, j, j_prime)] for j in self.params.J])

        for i in self.params.I:
            for j in self.params.J:
                self.grb.addSOS(GRB.SOS_TYPE1, [self.vars.Y_ijj[(i, j, j_prime)] for j_prime in self.params.J_star])

    def build_batch_can_not_be_own_successor(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_ijj[(i, j, j)] for j in self.params.J) == 0 for i in self.params.I )


    def build_batch_can_only_be_successor_if_there_is_predecessor(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_ijj[(i, j, j_star)] for j in self.params.J)
                           <= gp.quicksum(self.vars.Y_ijj[(i, j_star, j_prime)] for j_prime in self.params.J_star)
                              for j_star in self.params.J for i in self.params.I)

    def build_last_batch_is_zero(self):
        self.grb.addConstrs(gp.quicksum(self.vars.Y_ijj[(i, j, 0)] for j in self.params.J) \
                           >= gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)] for j in self.params.J)
                              for j_prime in self.params.J for i in self.params.I)

    def build_avoid_circle_sequence(self):
        self.grb.addConstrs(self.vars.Y_ijj[(i, j, j_prime)] + self.vars.Y_ijj[(i, j_prime, j)] <= 1
                              for i in self.params.I for j in self.params.J for j_prime in self.params.J)

    def build_start_time_zero_if_batch_not_active(self):
        self.grb.addConstrs(self.vars.U_j[j] <= self.params.q * gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)]
                                                    for i in self.params.I for j_prime in self.params.J_star)
                              for j in self.params.J)

    def build_start_time_batch_after_predecessor(self):
        self.grb.addConstrs(self.vars.U_j[j_prime] >= self.vars.U_j[j] + self.vars.e_j[j]
                              + self.params.s_b * gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)] for i in self.params.I)
                              + self.params.s_m * self.params.S_jj.get((j, j_prime), 0)
                              * gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)] for i in self.params.I)
                              - self.params.q*(1 - gp.quicksum(self.vars.Y_ijj[(i, j, j_prime)] for i in self.params.I))
                              for j in self.params.J for j_prime in self.params.J if j != j_prime)

class ConstraintsMultiSite(ConstraintsSite):
    def __init__(self):
        self.vars = None
        self.params = None
        self.grb = None

    def build_due_date_batch(self):
        self.grb.addConstrs(self.vars.T_j[j]
                          <= self.params.t_p[p] - self.params.B_jp[(j, p)] - self.vars.e_j[j]
                           + self.params.q * (1 - self.vars.F_jp[(j, p)])
                           for j in self.params.J for p in self.params.P)






