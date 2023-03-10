import numpy as np


class Parameters:
    def __init__(self, df_parts, input_dfs):
        self.r = input_dfs.sr_parameters['resolution']
        self.start_date = input_dfs.sr_parameters['start_date']
        self.psi = input_dfs.sr_parameters['psi']
        self.omega = input_dfs.sr_parameters['omega']
        self.rho_hour = self.rho / 365.0 / 24.0
        self.df_parts = df_parts
        self.input_dfs = input_dfs
        self.f_pc = input_dfs.sr_parameters['print_chamber_x_length']
        self.g_pc = input_dfs.sr_parameters['print_chamber_y_width']
        self.print_area = self.f_pc * self.g_pc

        self.w_powder = input_dfs.sr_parameters['max_speed_z'] / 3600.0
        self.w_laser = input_dfs.sr_parameters['max_speed_xy'] / 3600.0

        self.E_jm = self.create_E_jm()
        self.number_of_batches = len(set(list(zip(*self.E_jm.keys()))[0]))
        self.J = range(1, self.number_of_batches+1)
        self.J_star = range(0, self.number_of_batches+1)

        self.S_jj = self.create_S_jj()

        self.P = self.df_parts['part_id'].to_list()
        self.M = self.df_parts['material_id'].unique().tolist()

        self.number_of_parts = len(self.P)
        self.number_of_batches = len(self.J)
        self.number_of_materials = len(self.M)

        self.t_p = {}
        self.v_p = {}
        self.f_p = {}
        self.g_p = {}
        self.h_p = {}
        self.a_p = {}
        self.n_p = {}
        self.chi_p = {}
        self.B_p = {}
        self.A_mp = {}
        for part in df_parts.iterrows():
            p = part[1]['part_id']
            self.t_p[p] = (part[1]['due_date'].timestamp() - self.start_date.timestamp()) / 3600.0
            self.v_p[p] = part[1]['price']
            self.f_p[p] = part[1]['length']
            self.g_p[p] = part[1]['width']
            self.h_p[p] = part[1]['height']
            self.a_p[p] = self.f_p[p] * self.g_p[p]
            self.n_p[p] = part[1]['material_id']
            destination_p = part[1]['destination']
            self.B_p[p] = float(input_dfs.df_transport[input_dfs.df_transport['destination'] == destination_p]
                                [self.location]) * 24
            self.chi_p[p] = self.v_p[p] * self.psi + self.omega * self.B_p[p]
            m = part[1]['material_id']
            self.A_mp[(m, p)] = 1

        self.m_j = {}
        for j in self.J:
            for m in self.M:
                if self.E_jm.get((j, m), 0) == 1:
                    self.m_j[j] = m

        self.q = max(max(self.t_p.values()), self.f_pc, self.g_pc)

        self.pp_list_material = []
        for p in self.P:
            for p_tick in self.P:
                if p != p_tick and self.n_p[p] == self.n_p[p_tick]:
                    self.pp_list_material.append((p, p_tick))

        self.list_jj_tick = [(j, j_tick) for j in self.J for j_tick in self.J_star]
        self.list_pp_tick = [(p, p_tick) for p in self.P for p_tick in self.P]
        self.list_jp = [(j, p) for j in self.J for p in self.P]
        self.list_pp_tick = [(p, p_tick) for p in self.P for p_tick in self.P]
        self.neg_jp_list_material = [(j, p) for j in self.J for p in self.P for m in self.M
                                     if self.A_mp.get((m, p), 0) * self.E_jm.get((j, m), 0) == 1]
        self.jp_list_material = [jp for jp in self.list_jp if jp not in self.neg_jp_list_material]


    def create_S_jj(self):
        E_j = {0: -1}
        for key in self.E_jm.keys():
            if self.E_jm.get(key, 0) == 1:
                E_j[key[0]] = key[1]
        S_jj_tick = {}
        for j in self.J:
            for j_prime in self.J_star:
                if E_j[j] != E_j[j_prime]:
                    S_jj_tick[(j, j_prime)] = 1
        return S_jj_tick

    def create_E_jm(self):
        materials = self.df_parts['material_id'].unique().tolist()
        number_of_batches_for_each_material = {}
        for m in materials:
            df_parts_with_material = self.df_parts[self.df_parts['material_id'] == m]
            area_of_materials = (df_parts_with_material['width'] * df_parts_with_material['length']).sum()
            number_of_batches = int(np.floor(area_of_materials / self.print_area * 2) + 2)
            number_of_batches_for_each_material[m] = number_of_batches
        E_jm = {}
        j = 1
        for m in materials:
            for pseudo_j in range(number_of_batches_for_each_material[m]):
                E_jm[(j, m)] = 1
                j += 1
        return E_jm




class ParametersSite(Parameters):
    def __init__(self, df_parts, input_dfs, site):
        self.location = site['location']

        self.number_of_machines = site['number_of_machines']
        self.rho = site['inventory_cost_factor']
        self.tau = site['production_cost_factor']
        self.sigma = site['setup_cost_factor']
        self.s_b = site['setup_time_batching']
        self.s_m = site['setup_time_material']
        self.I = range(0, self.number_of_machines)
        Parameters.__init__(self, df_parts, input_dfs)
        self.list_ijj_tick = [(i, j, j_tick) for i in self.I for j in self.J for j_tick in self.J_star]

class ParametersMultiSite(ParametersSite):
    def __init__(self, input_dfs):
        df_parts = input_dfs.df_parts
        """AS THIS IS ONLY A TEST JUST USE THE FIRST SITE"""
        site = input_dfs.df_sites.iloc[0]
        ParametersSite.__init__(self, df_parts, input_dfs, site)

        self.B_jp = {}
        self.chi_jp = {}
        self.C_ij = {}
        self.E_jm = {}
        self.create_C_ij_E_jm()

        for part in df_parts.iterrows():
            p = part[1]['part_id']
            destination_p = part[1]['destination']
            for machine in input_dfs.df_machines.iterrows():
                location = machine[1]['location']
                i = machine[1]['unique_machine_id']
                for j in self.J:
                    if self.C_ij.get((i, j), 0) == 1:
                        self.B_jp[(j, p)] = float(input_dfs.df_transport[input_dfs.df_transport['destination'] == destination_p]
                                            [location]) * 24
                        self.chi_jp[(j, p)] = self.v_p[p] * self.psi + self.omega * self.B_jp[(j, p)]


    def create_C_ij_E_jm(self):
        materials = self.df_parts['material_id'].unique().tolist()
        number_of_batches_for_each_material = {}
        for m in materials:
            df_parts_with_material = self.df_parts[self.df_parts['material_id'] == m]
            area_of_materials = (df_parts_with_material['width'] * df_parts_with_material['length']).sum()
            number_of_batches = int(np.floor(area_of_materials / self.print_area * 2) + 2)
            number_of_batches_for_each_material[m] = number_of_batches
        j = 1
        for i in self.I:
            for m in materials:
                for pseudo_j in range(number_of_batches_for_each_material[m]):
                    self.E_jm[(j, m)] = 1
                    self.C_ij[(i, j)] = 1
                    j += 1


class ParametersMachine(Parameters):
    def __init__(self, df_parts, input_dfs, machine):
        self.location = machine['location']
        self.rho = machine['inventory_cost_factor']
        self.tau = machine['production_cost_factor']
        self.sigma = machine['setup_cost_factor']
        self.s_b = machine['setup_time_batching']
        self.s_m = machine['setup_time_material']
        self.I = None
        Parameters.__init__(self, df_parts, input_dfs)


class ParametersALNS(Parameters):
    def __init__(self, df_parts, input_dfs, machine):
        Parameters.__init__(self, df_parts, input_dfs)
        self.location = machine['location']
        self.rho = machine['inventory_cost_factor']
        self.tau = machine['production_cost_factor']
        self.sigma = machine['setup_cost_factor']
        self.s_b = machine['setup_time_batching']
        self.s_m = machine['setup_time_material']
        self.I = None
        self.J = None
        self.number_of_batches = 0
