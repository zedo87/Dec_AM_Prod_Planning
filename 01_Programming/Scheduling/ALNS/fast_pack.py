import pandas as pd

class FastPack:
    def __init__(self, params, variables):
        self.vars = variables
        self.params = params

    def fast_packing(self, pi):
        """
        :param pi: permutation of part list
        :return: a batching configuration F_jp
        """
        for part_id in pi.copy():
            for O in self.vars.df_O.df_iterrows():
                sr_O = O[1]
                feasible = self.check_if_part_feasible(part_id, sr_O)
                if feasible:
                    old_O = sr_O.copy()
                    self.place_part_in_batch(part_id, old_O)
                    self.drop_corner_point_O(old_O)
                    self.add_corner_point_to_df_O(part_id, old_O)
                    self.sort_df_O()
                    self.open_batch_if_new_batch_required()
                    break

    def get_parts_of_batch(self, j):
        """
        return set of parts which are placed within j
        :param j:
        :return:
        """
        keys = self.vars.F_jp.keys()
        j_s = list(zip(*keys))[0]
        p_s = list(zip(*keys))[1]
        indices_j = [index for index, value in enumerate(j_s) if value == j]
        P_j = set([p_s[index] for index in indices_j])
        return P_j

    def check_batch_feasible(self, j):
        """
        checks if placement of parts are feasible for this batch
        :param j: batch_id (integer)
        :return: boolean True-> batch is feasible, False -> not feasible
        """
        P_j = self.get_parts_of_batch(j)
        feasible = True
        for p in P_j:
            for p_prime in P_j:
                if p > p_prime:
                    w_f_pc = round((self.vars.x_p[p] + self.params.f_p[p]), 1) <= round(self.params.f_pc, 1)
                    w_g_pc = round((self.vars.y_p[p] + self.params.g_p[p]), 1) <= round(self.params.g_pc, 1)
                    w_pp_1 = round((self.vars.x_p[p] + self.params.f_p[p]), 1) <= round(self.vars.x_p[p_prime], 1)
                    w_pp_2 = round((self.vars.x_p[p_prime] + self.params.f_p[p_prime]), 1) <= round(
                        self.vars.x_p[p], 1)
                    w_pp_3 = round((self.vars.y_p[p] + self.params.g_p[p]), 1) <= round(self.vars.y_p[p_prime], 1)
                    w_pp_4 = round((self.vars.y_p[p_prime] + self.params.g_p[p_prime]), 1) <= round(
                        self.vars.y_p[p], 1)
                    feasible = w_f_pc and w_g_pc and (w_pp_1 or w_pp_2 or w_pp_3 or w_pp_4)
                    if not feasible: break
            if not feasible: break
        return feasible

    def check_if_part_feasible(self, p, sr_O):
        """
        checks if placement of parts are feasible for this batch
        :param sr_O: batch_id (integer)
        :param p = part_id
        :return: boolean True-> batch is feasible, False -> not feasible
        """
        j = sr_O['j']
        P_j = self.get_parts_of_batch(j)
        feasible = True
        for p_prime in P_j:
            w_f_pc = round((self.vars.x_p[p] + self.params.f_p[p]), 1) <= round(self.params.f_pc, 1)
            w_g_pc = round((self.vars.y_p[p] + self.params.g_p[p]), 1) <= round(self.params.g_pc, 1)
            w_pp_1 = round((self.vars.x_p[p] + self.params.f_p[p]), 1) <= round(self.vars.x_p[p_prime], 1)
            w_pp_2 = round((self.vars.x_p[p_prime] + self.params.f_p[p_prime]), 1) <= round(self.vars.x_p[p], 1)
            w_pp_3 = round((self.vars.y_p[p] + self.params.g_p[p]), 1) <= round(self.vars.y_p[p_prime], 1)
            w_pp_4 = round((self.vars.y_p[p_prime] + self.params.g_p[p_prime]), 1) <= round(self.vars.y_p[p], 1)
            feasible = w_f_pc and w_g_pc and (w_pp_1 or w_pp_2 or w_pp_3 or w_pp_4)
            if not feasible: break
        return feasible

    def check_corner_point_feasible(self, sr_O):
        """
        checks if position of corner does not lie within a part
        :param sr_O: is the row of all corner points. Consists of batch, j and position x_x
        :return: True if corner is not in part, False if it is within a part (not feasible)
        """
        j = sr_O['y']
        x = sr_O['x']
        y = sr_O['y']
        P_j = self.get_parts_of_batch(j)

        feasible = True
        for p in P_j:
            w_f_pc = round(x, 1) <= round(self.params.f_pc, 1)
            w_g_pc = round(y, 1) <= round(self.params.g_pc, 1)
            w_pp_1 = round((self.vars.x_p[p] + self.params.f_p[p]), 1) <= round(x, 1)
            w_pp_2 = round((self.vars.x_p[p]), 1) >= round(x, 1)
            w_pp_3 = round((self.vars.y_p[p] + self.params.g_p[p]), 1) <= round(y, 1)
            w_pp_4 = round((self.vars.y_p[p]), 1) >= round(y, 1)
            feasible = w_f_pc and w_g_pc and (w_pp_1 or w_pp_2 or w_pp_3 or w_pp_4)
            if not feasible: break
        return feasible

    def add_corner_point_to_df_O(self, p, old_sr_O):
        """
        adds two new corner points
        :param j: batch_id
        :param O_xy: tuple (x,y) of corner point
        :param p: part_id
        :return:
        """
        j = old_sr_O['j']
        O_new_1 = pd.Series({'x': (old_sr_O['x'] + self.params.x_p[p]),
                             'y': old_sr_O['y'],
                             'j': j})
        if self.check_corner_point_feasible(O_new_1):
            self.vars.df_O[j] = pd.concat([self.vars.df_O[j], O_new_1.to_frame().T], ignore_index=True)

        O_new_2 = pd.Series({'x': old_sr_O['x'],
                             'y': (old_sr_O['y'] + + self.params.y_p[p]),
                             'j': j})
        if self.check_corner_point_feasible(O_new_2):
            self.vars.df_O[j] = pd.concat([self.vars.df_O[j], O_new_2.to_frame().T], ignore_index=True)

    def place_part_in_batch(self, p, sr_O):
        """
        places part in batch j, sets part/batch combinatio (F_jp), sets position x_p and y_p and sets Y_jj
        -> as sequence is fixed (j always comes before j+1) we can set predecessor und successor
        :param p:  part_id
        :param j:  batch_id
        :param O: corner point of new position tuple dict key=O_index (o) value=(x_p, y_p)
        :return:
        """
        j = sr_O['j']
        self.vars.F_jp[(j, p)] = 1
        self.vars.x_p = sr_O['x']
        self.vars.y_p = sr_O['y']
        self.vars.Y_jj[(j, j + 1)] = 1

    def sort_df_O(self):
        self.vars.df_O_j = self.vars.df_O_j.sort_values(['j', 'y', 'x'])

    def drop_corner_point_O(self, sr_O):
        dropped = self.vars.df_O.drop(self.vars.df_O[self.vars.df_O[['j', 'x', 'y']] == sr_O].index, inplace=True)
        assert dropped is True

    def open_batch_if_new_batch_required(self):
        """
        the last batch must always be an empty batch with coordinates x,y = (0,0). if it is not the case, open a batch
        :return:
        """
        self.sort_df_O()
        x = self.vars.df_O.iloc[-1]['x']
        y = self.vars.df_O.iloc[-1]['x']
        if not (x == 0 and y == 0):
            self.open_new_batch()

    def open_new_batch(self):
        """
        appends a row to df_O, with the next batch, and a new corner point at the origin, at x=0, y=0
        :return:
        """
        highest_j = self.vars.df_O['j'].max()
        new_j = highest_j + 1
        sr_new_O = pd.Series({'j': new_j,
                              'x': 0,
                              'y': 0})
        self.vars.df_O = pd.concat([self.vars.df_O, sr_new_O.to_frame().T], ignore_index=True)

    """
    def create_random_permutation_of_parts(self, seed):
        rd.seed(seed)
        self.vars.pi = list(self.params.P).copy()
        rd.shuffle(self.vars.pi)
    """
