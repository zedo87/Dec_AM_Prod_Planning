from variables import VariablesALNS
from Scheduling.parameters import ParametersMachine

class ModelMachineALNS:
    def __init__(self, input_dfs):
        self.params = ParametersMachine(input_dfs.df_parts, input_dfs, input_dfs.df_machines.iloc[0])
        self.vars = VariablesALNS()



