from Scheduling.LP.constraints import ConstraintsSite, ConstraintsMachine, ConstraintsMultiSite
from Scheduling.LP.objective_function import ObjectiveFunctionSite, ObjectiveFunctionMachine, ObjectiveFunctionMultiSite
from Scheduling.LP.variables import VariablesSite, VariablesMachine

class ModelSite(ConstraintsSite, ObjectiveFunctionSite):
    def __init__(self, params, grb_model):
        self.params = params
        self.grb = grb_model
        self.vars = VariablesSite(params, grb_model)


class ModelMultiSite(ConstraintsMultiSite, ObjectiveFunctionMultiSite):
    def __init__(self, params, grb_model):
        self.params = params
        self.grb = grb_model
        self.vars = VariablesSite(params, grb_model)


class ModelMachine(ConstraintsMachine, ObjectiveFunctionMachine):
    def __init__(self, params, grb_model):
        self.params = params
        self.grb = grb_model
        self.vars = VariablesMachine(params, grb_model)
