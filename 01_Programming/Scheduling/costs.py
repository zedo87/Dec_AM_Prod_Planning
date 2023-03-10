import pandas as pd

class Costs:
    def __init__(self, model):
        self.costs_solver = None
        if model:
            self.costs_solver = model.grb.ObjVal
        else:
            self.costs_solver = 0

    def post_processing_costs(self):
        """
        if solved succesfully (in or over time limit use, solution of solver for costs.)
        if there is no model --> meaning there are no parts for this instance --> set costs to zero
        if solver was not solved succesfully, set costs to max
        :return:
        """
        if self.solver_successful:
            if self.model:
                setup_costs = self.compute_setup_costs()
                production_costs = self.compute_production_costs()
                inventory_costs = self.compute_inventory_costs()
                transport_costs = self.compute_transport_costs()
                sum_costs = setup_costs + production_costs + transport_costs + inventory_costs
                self.costs = pd.Series({
                    "SUM": sum_costs,
                    "SUM_SOLV": self.costs_solver,
                    "PROD": production_costs,
                    "TRANS": transport_costs,
                    "SET": setup_costs,
                    "INV": inventory_costs})
            else:
                self.set_zero_sr_costs()
        else:
            self.set_max_sr_cost()

    def compute_inventory_costs(self):
        inventory_costs = 0
        for p in self.model.params.P:
            inventory_costs += self.model.params.rho_hour * self.model.params.v_p[p] \
                             * (self.model.params.t_p[p] - self.z_p[p])
        return inventory_costs

    def set_max_sr_cost(self):
        q = 99999.0
        if self.costs is None:
            self.costs = pd.Series({
                'SUM': q,
                'SUM_SOLV': q,
                'PROD': q,
                'TRANS': q,
                'SET': q,
                'INV': q})
        else:
            self.costs['SUM'] = q
            self.costs['SUM_SOLV'] = q
            self.costs['PROD'] = q
            self.costs['TRANS'] = q
            self.costs['SET'] = q
            self.costs['INV'] = q


    def set_zero_sr_costs(self):
        self.costs = pd.Series({
            'SUM': 0.0,
            'SUM_SOLV': 0.0,
            'PROD': 0.0,
            'TRANS': 0.0,
            'SET': 0.0,
            'INV': 0.0})

    def compute_production_costs(self):
        production_costs = 0
        for j in self.model.params.J:
            production_costs += self.e_j[j] * self.model.params.tau
        return production_costs

    def compute_transport_costs(self):
        transport_costs = 0
        for p in self.model.params.P:
            transport_costs += self.model.params.chi_p[p]
        return transport_costs

    def set_attributes_of_bid(self, bid):
        self.costs['bundle'] = bid['bundle']
        self.costs['unique_machine_id'] = bid['unique_machine_id']
        self.costs['machine_id'] = bid['machine_id']
        self.costs['site'] = bid['site']
        self.costs['solver_successful'] = False

    def set_location(self, location):
        self.costs['location'] = location

    def set_site_id(self, site):
        self.costs['site'] = site

    def compute_setup_costs(self):
        pass


class CostsMachine(Costs):
    def __init__(self, model):
        Costs.__init__(self, model)

    def compute_setup_costs(self):
        setup_costs = 0
        number_of_batches = 0
        for j in self.model.params.J:
            for j_prime in self.model.params.J_star:
                if self.Y_jj[(j, j_prime)] == 1:
                    number_of_batches += 1
                    setup_costs += self.Y_jj[(j, j_prime)] * self.model.params.sigma * self.model.params.s_b
                    setup_costs += self.Y_jj[(j, j_prime)] * self.model.params.S_jj.get((j, j_prime), 0) \
                                 * self.model.params.sigma * self.model.params.s_m
        return setup_costs

    def set_unique_machine_id(self, unique_machine_id):
        self.costs['unique_machine_id'] = unique_machine_id

    def set_machine_id(self, machine_id):
        self.costs['machine_id'] = machine_id

    def set_bundle_id(self, bundle_id):
        self.costs['bundle_id'] = bundle_id

    def set_scenario_id(self, scenario_id):
        self.costs['scenario_id'] = scenario_id


class CostsSite(Costs):
    def __init__(self, model):
        Costs.__init__(self, model)

    def compute_setup_costs(self):
        setup_costs = 0
        number_of_batches = 0
        for j in self.model.params.J:
            for j_prime in self.model.params.J_star:
                for i in self.model.params.I:
                    if self.Y_ijj[(i, j, j_prime)] == 1:
                        number_of_batches += 1
                        setup_costs += self.Y_ijj[(i, j, j_prime)] * self.model.params.sigma * self.model.params.s_b
                        setup_costs += self.model.params.S_jj.get((j, j_prime), 0) * self.Y_ijj[(i, j, j_prime)] \
                                 * self.model.params.sigma * self.model.params.s_m
        return setup_costs

class CostsMultiSite(CostsSite):
    def __init__(self, model):
        CostsSite.__init__(self, model)

    def compute_transport_costs(self):
        transport_costs = 0
        for j in self.model.params.J:
            for p in self.model.params.P:
                transport_costs += self.model.params.chi_jp[(j,p)] * self.F_jp[(j, p)]
        return transport_costs










