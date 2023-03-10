from Post_Processing.gurobi_post_process import create_binary_solution_dict, create_solution_dict
import pandas as pd
from Scheduling.costs import CostsMachine, CostsSite, CostsMultiSite


class ResultSched:
    def __init__(self, model):
        self.model = model
        self.duration_sec = None
        self.seed = None
        self.result_id = None
        self.solution_found_status = {2, 9}
        if self.model:
            self.x_p = create_solution_dict(self.model.vars.x_p)
            self.y_p = create_solution_dict(self.model.vars.y_p)
            self.z_p = create_solution_dict(self.model.vars.z_p)
            self.e_j = create_solution_dict(self.model.vars.e_j)
            self.F_jp = create_binary_solution_dict(self.model.vars.F_jp)
            self.batch_p = self.create_batch_p()
            self.solver_status = self.model.grb.Status
            self.solver_successful = False
            if self.solver_status in self.solution_found_status:
                self.solver_successful = True
        else:
            self.solver_successful = True

    def create_batch_p(self):
        batch_p = {}
        for key in self.F_jp.keys():
            if self.F_jp.get(key, 0) == 1:
                batch_p[key[1]] = key[0]
        return batch_p

    def set_attributes_of_bid(self, bid):
        self.costs['bundle_id'] = bid['bundle_id']
        self.costs['unique_machine_id'] = bid['unique_machine_id']
        self.costs['machine_id'] = bid['machine_id']
        self.costs['site'] = bid['site']
        self.costs['solver_successful'] = False

    def get_e_j_post_process(self):
        for j in self.model.params.J:
            duration_height = self.get_e_j_height_post_process(j)
            duration_volume = self.get_e_j_volume_post_process(j)
            duration = duration_height +duration_volume
            print("e_j for batch %s is: %s" %(j, duration))

    def get_e_j_height_post_process(self, j):
        max_height_j = 0
        for p in self.model.params.P:
            if self.F_jp.get((j, p), 0) == 1:
                if max_height_j < self.model.params.h_p[p]:
                    max_height_j = self.model.params.h_p[p]
        duration = max_height_j / self.model.params.r * self.model.params.w_powder
        print("e_j_height for batch %s is: %s" %(j, duration))
        return duration

    def get_e_j_volume_post_process(self, j):
        volume = 0
        for p in self.model.params.P:
            if self.F_jp.get((j, p), 0) == 1:
                volume += self.model.params.h_p[p]\
                        * self.model.params.f_p[p] \
                        * self.model.params.g_p[p]
        duration = volume / self.model.params.r * self.model.params.w_laser
        print("e_j_volume for batch %s is: %s" % (j, duration))
        return duration

    def set_duration_sec(self, duration_sec):
        self.duration_sec = duration_sec

    def set_seed(self, seed):
        self.seed = seed

    def set_result_id(self, result_id):
        self.result_id = result_id


class ResultSchedMachine(CostsMachine, ResultSched):
    def __init__(self, model=None):
        CostsMachine.__init__(self, model)
        ResultSched.__init__(self, model)
        if model:
            self.Y_jj = create_binary_solution_dict(model.vars.Y_jj)
        self.post_processing_costs()

    def get_solution_to_parts_df(self):
        df_parts = pd.DataFrame()
        for j in self.model.params.J:
            for p in self.x_p.keys():
                if self.F_jp.get((j, p), 0) == 1:
                    sr_part_result = pd.Series({
                        'batch_id': j,
                        'part_id': p,
                        'x_p': self.x_p[p],
                        'y_p': self.y_p[p]})
                    df_parts = pd.concat([df_parts, sr_part_result.to_frame().T], ignore_index=True)
        return df_parts


class ResultSchedSite(CostsSite, ResultSched):
    def __init__(self, model=None, set_high_bid=False):
        CostsSite.__init__(self, model)
        ResultSched.__init__(self, model)
        if model:
            self.Y_ijj = create_binary_solution_dict(model.vars.Y_ijj)
            self.Y_ij = self.create_Y_ij()
        self.post_processing_costs()
        if set_high_bid:  self.set_max_sr_cost()

    def create_Y_ij(self):
        Y_ij = {}
        for key in self.Y_ijj.keys():
            if self.Y_ijj[key] == 1:
                Y_ij[(key[0], key[1])] = 1
        return Y_ij

    def get_solution_to_parts_df(self):
        df_parts = pd.DataFrame()
        for (i, j) in self.Y_ij.keys():
            if self.Y_ij[(i, j)] == 1:
                for p in self.x_p.keys():
                    if self.F_jp.get((j, p), 0) == 1:
                        sr_part_result = pd.Series({
                            'site_machine_id': i,
                            'batch_id': j,
                            'part_id': p,
                            'x_p': self.x_p[p],
                            'y_p': self.y_p[p]})
                        df_parts = pd.concat([df_parts, sr_part_result.to_frame().T], ignore_index=True)
        return df_parts

class ResultSchedMultiSite(CostsMultiSite, ResultSched):
    def __init__(self, model=None, set_high_bid=False):
        CostsSite.__init__(self, model)
        ResultSched.__init__(self, model)
        if model:
            self.Y_ijj = create_binary_solution_dict(model.vars.Y_ijj)
            self.Y_ij = self.create_Y_ij()
        self.post_processing_costs()
        if set_high_bid: self.set_max_sr_cost()

    def create_Y_ij(self):
        Y_ij = {}
        for key in self.Y_ijj.keys():
            if self.Y_ijj[key] == 1:
                Y_ij[(key[0], key[1])] = 1
        return Y_ij

    def get_solution_to_parts_df(self):
        df_parts = pd.DataFrame()
        for (i, j) in self.Y_ij.keys():
            if self.Y_ij[(i, j)] == 1:
                for p in self.x_p.keys():
                    if self.F_jp.get((j, p), 0) == 1:
                        sr_part_result = pd.Series({
                            'site_machine_id': i,
                            'batch_id': j,
                            'part_id': p,
                            'x_p': self.x_p[p],
                            'y_p': self.y_p[p]})
                        df_parts = pd.concat([df_parts, sr_part_result.to_frame().T], ignore_index=True)
        return df_parts

