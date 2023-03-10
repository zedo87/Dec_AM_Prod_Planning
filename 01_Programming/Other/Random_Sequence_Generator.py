# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 14:36:09 2022

@author: dozehetner
"""
import gurobipy as gp
from gurobipy import GRB
import pandas as pd
from itertools import product
import scipy.sparse as sp
import numpy as np
    
def create_structured_random_sequences(list_IDs, number_of_groups):
    number_of_parts = len(list_IDs)
    n = number_of_groups
    number_of_sequences = number_of_parts*number_of_groups
    
    q = 9999
    
    K = range(0,number_of_sequences)
    I = range(0,number_of_parts)
    J = list(list_IDs)
    
    pd_I = pd.DataFrame(I, columns=["i"])
    pd_J = pd.DataFrame(J, columns=["j"])
    pd_K = pd.DataFrame(K, columns=["k"])
    
    pd_variables_x = pd.DataFrame(data=list(product(pd_I['i'], pd_J['j'],pd_K['k'])), columns=['i','j', "k"]).reset_index().rename(columns={"index":"var_index"})
    pd_variables_y = pd.DataFrame(data=list(product(pd_K['k'], pd_K['k'])), columns=["k","k_tick"]).reset_index().rename(columns={"index":"var_index"})
    
    pd_eq_1_rhs = pd.DataFrame(data=list(product(pd_J['j'], pd_K['k'])), columns=['j','k']).reset_index().rename(columns={"index":"row_index"})
    pd_eq_1_rhs["rhs"] = 1
    
    pd_eq_1_x_ijk = pd_eq_1_rhs[["j","k", "row_index"]]
    pd_eq_1_x_ijk = pd.merge(pd_eq_1_x_ijk, pd_variables_x, how="left", left_on=["j","k"], right_on=["j","k"])
    pd_eq_1_x_ijk["values"] = 1
    
    pd_eq_2_rhs = pd.DataFrame(data=list(product(pd_I['i'], pd_K['k'])), columns=['i','k']).reset_index().rename(columns={"index":"row_index"})
    pd_eq_2_rhs["rhs"] = 1
    
    pd_eq_2_x_ijk = pd_eq_2_rhs[["i","k", "row_index"]]
    pd_eq_2_x_ijk = pd.merge(pd_eq_2_x_ijk, pd_variables_x, how="left", left_on=["i","k"], right_on=["i","k"])
    pd_eq_2_x_ijk["values"] = 1
    
    pd_eq_3_rhs = pd.DataFrame(data=list(product(pd_I['i'], pd_J['j'])), columns=['i','j']).reset_index().rename(columns={"index":"row_index"})
    pd_eq_3_rhs["rhs"] = n
    
    pd_eq_3_x_ijk = pd_eq_3_rhs[["i", "j", "row_index"]]
    pd_eq_3_x_ijk = pd.merge(pd_eq_3_x_ijk, pd_variables_x, how="left", left_on=["i","j"], right_on=["i","j"])
    pd_eq_3_x_ijk["values"] = 1
    
    pd_eq_4_rhs = pd.DataFrame(data=list(product(pd_I['i'], pd_J['j'], pd_K['k'], pd_K['k'])), columns=['i','j', 'k', 'k_tick']).reset_index().rename(columns={"index":"row_index"})
    pd_eq_4_rhs["rhs"] = 1
    
    pd_eq_4_x_ijk = pd_eq_4_rhs
    pd_eq_4_x_ijk = pd.merge(pd_eq_4_x_ijk, pd_variables_x, how="left", left_on=["i","j","k"], right_on=["i","j","k"])
    pd_eq_4_x_ijk["values"] = 1
    
    pd_eq_4_x_ijk_tick = pd_eq_4_rhs
    pd_eq_4_x_ijk_tick = pd.merge(pd_eq_4_x_ijk_tick, pd_variables_x, how="left", left_on=["i","j","k_tick"], right_on=["i","j","k"])
    pd_eq_4_x_ijk_tick["values"] = 1
    
    pd_eq_4_y_kk = pd_eq_4_rhs
    pd_eq_4_y_kk = pd.merge(pd_eq_4_y_kk, pd_variables_y, how="left", left_on=["k","k_tick"], right_on=["k","k_tick"])
    pd_eq_4_y_kk["values"] = q
    
    pd_eq_4_x_ijk = pd.concat([pd_eq_4_x_ijk, pd_eq_4_x_ijk_tick], ignore_index=True)
    
    pd_eq_5_rhs = pd.DataFrame(data=list(product(pd_K['k'], pd_K['k'])), columns=['k', 'k_tick']).reset_index().rename(columns={"index":"row_index"})
    pd_eq_5_rhs["rhs"] = 1
    
    pd_eq_5_y_kk = pd_eq_5_rhs
    pd_eq_5_y_kk = pd.merge(pd_eq_5_y_kk, pd_variables_y, how="left", left_on=["k","k_tick"], right_on=["k","k_tick"])
    pd_eq_5_y_kk["values"] = 1
    
    model = gp.Model("random_number")
    model.Params.LogToConsole = 0
    
    #------create Variables
    
    x_ijk = model.addMVar(len(pd_variables_x), vtype=GRB.BINARY, name="x_ijk")
    y_kk_tick = model.addMVar(len(pd_variables_y), vtype=GRB.BINARY, name="y_kk_tick")
    
    #------create Constraints
    
    #-------EQ 1
    
    rows = list(pd_eq_1_x_ijk["row_index"])
    cols = list(pd_eq_1_x_ijk["var_index"])
    values = list(pd_eq_1_x_ijk["values"])
    
    A_rows = len(pd_eq_1_rhs)
    A_cols = len(pd_variables_x)
    
    A = sp.coo_matrix((values, (rows, cols)), shape=(A_rows, A_cols))
    b = np.array(pd_eq_1_rhs["rhs"]).T
    model.addConstr(A @ x_ijk ==b)
    model.update()
    #-------EQ 2 
    
    rows = list(pd_eq_2_x_ijk["row_index"])
    cols = list(pd_eq_2_x_ijk["var_index"])
    values = list(pd_eq_2_x_ijk["values"])
    
    A_rows = len(pd_eq_2_rhs)
    A_cols = len(pd_variables_x)
    
    A = sp.coo_matrix((values, (rows, cols)), shape=(A_rows, A_cols))
    b = np.array(pd_eq_2_rhs["rhs"]).T
    model.addConstr(A @ x_ijk ==b)
    model.update()
    
    #-------EQ 3
    
    rows = list(pd_eq_3_x_ijk["row_index"])
    cols = list(pd_eq_3_x_ijk["var_index"])
    values = list(pd_eq_3_x_ijk["values"])
    
    A_rows = len(pd_eq_3_rhs)
    A_cols = len(pd_variables_x)
    
    A = sp.coo_matrix((values, (rows, cols)), shape=(A_rows, A_cols))
    b = np.array(pd_eq_3_rhs["rhs"]).T
    model.addConstr(A @ x_ijk ==b)
    model.update()
    
    
    #---------EQ 4
    
    rows = list(pd_eq_4_x_ijk["row_index"])
    cols = list(pd_eq_4_x_ijk["var_index"])
    values = list(pd_eq_4_x_ijk["values"])
    
    A_rows = len(pd_eq_4_rhs)
    A_cols = len(pd_variables_x)
    
    A_xijk = sp.coo_matrix((values, (rows, cols)), shape=(A_rows, A_cols))
    
    rows = list(pd_eq_4_y_kk["row_index"])
    cols = list(pd_eq_4_y_kk["var_index"])
    values = list(pd_eq_4_y_kk["values"])
    
    A_rows = len(pd_eq_4_rhs)
    A_cols = len(pd_variables_y)
    
    A_y_kk = sp.coo_matrix((values, (rows, cols)), shape=(A_rows, A_cols))
    
    b = np.array(pd_eq_4_rhs["rhs"]).T
    model.addConstr(A_xijk @ x_ijk + A_y_kk @ y_kk_tick >=b)
    model.update()
    
    #------------ EQ 5
    
    rows = list(pd_eq_5_y_kk["row_index"])
    cols = list(pd_eq_5_y_kk["var_index"])
    values = list(pd_eq_5_y_kk["values"])
    
    A_rows = len(pd_eq_5_rhs)
    A_cols = len(pd_variables_y)
    
    A = sp.coo_matrix((values, (rows, cols)), shape=(A_rows, A_cols))
    b = np.array(pd_eq_5_rhs["rhs"]).T
    model.addConstr(A @ y_kk_tick >=b)
    model.Params.LogToConsole = 0
    
    model.update()
    model.optimize()
    
    pd_variables_x["solution"] = x_ijk.X
    
    sequences = []
    for k in K: 
        sequences.append(list(pd_variables_x[(pd_variables_x["solution"]==1.0) & (pd_variables_x["k"]==k)].sort_values("i")["j"]))
    return sequences