from Input.file_management import *
from Scheduling.ALNS.ALNS_for_material import ALNS_material

if __name__ == "__main__":

    absolut_path_file = "C:/Users/dozehetner/Seafile/03_Research/09_DecPlanning_ML_Support/04_Experiments" \
                       "/02_Case_Study_Submission/01_Input_Data/S1I01.xlsx"
    input_dfs = InputDataFrames(absolut_path_file)
    solver = ALNS_material(input_dfs)
    solver.solve()



