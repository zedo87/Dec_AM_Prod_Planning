
class Costs:
    def __init__(self):
        self.TRANS = 0
        self.PROD = 0
        self.SET = 0
        self.INV = 0
        self.TOTAL = 0

    def compute_inventory_costs(self):
        pass

    def compute_production_costs(self):
        pass

    def compute_transportation_costs(self):
        pass

    def compute_setup_costs(self):
        pass

    def compute_costs(self):
        self.compute_transportation_costs()
        self.compute_inventory_costs()
        self.compute_production_costs()
        self.compute_setup_costs()
        self.TOTAL = self.TRANS +  self.PROD + self.SET + self.INV
