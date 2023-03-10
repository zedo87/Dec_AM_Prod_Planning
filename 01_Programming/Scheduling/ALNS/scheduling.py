from operator import itemgetter
import numpy as np
from math import inf

class Scheduling:
    def determine_e_j(self):
        """
        e_j is the production duration for each batch.
        :return:
        """
        for j in self.vars.J:
            h_max = 0
            volume = 0
            for p in self.vars.P_j[j]:
                volume += self.params.f_p[p] \
                          * self.params.g_p[p] \
                          * self.params.h_p[p]

                if h_max < self.params.h_p[p]:
                    h_max = self.params.h_p[p]
            self.vars.e_j[j] = h_max / self.params.r * self.params.w_powder \
                               + volume / self.params.r * self.params.w_laser


    def set_part_batch_config_P_j(self):
        """
        as a dictionary is more convinient in this case, we convert F_jp to P_j. P_j is a dictionary in which the
        key is defined by the batch j and points to a set of parts.
        :return:
        """
        for (j, p) in self.vars.F_jp.keys():
            if self.vars.F_jp.get((j, p), 0) == 1:
                if self.vars.P_j.get(j, None) is None:
                    self.vars.P_j[j] = {p}
                else:
                    self.vars.P_j[j] = self.vars.P_j[j].add(p)


    def create_batch_list(self):
        """ Actually, J is a variable in this algorithm. In order to remain the same datastructure J is also written on
        params.J
        """
        self.vars.J = sorted(list(set(list(zip(*self.vars.F_jp))[0])))
        self.params.J = self.vars.J


    def schedule(self):
        for j in self.vars.J:
            P_j = self.get_parts_of_batch(j)
            t_p_J = np.array(itemgetter(*P_j)(self.params.t_p))
            chi_p_J = np.array(itemgetter(*P_j)(self.params.chi_p))
            end_date_batch = min(max(t_p_J - chi_p_J),
                                 self.vars.U_j.get(j - 1, inf))
            self.vars.U_j[j] = end_date_batch - self.vars.e_j[j]
            for p in P_j:
                self.z_p[p] = end_date_batch
