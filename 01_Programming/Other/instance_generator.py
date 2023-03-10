# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 15:01:09 2022

@author: dozehetner
"""

import pandas as pd
import random
import os
import numpy as np

input_data = pd.read_excel("C:/Users/dozehetner/Seafile/03_Research/02_Decentralized_Planning/03_Programming/01_Input_Data/Input_data_2.xlsx", sheet_name="Input Data")
df_transport_matrix = pd.read_csv("C:/Users/dozehetner/Seafile/03_Research/02_Decentralized_Planning/03_Programming/01_Input_Data/transport_matrix_ABC.csv", sep=";")
number_of_parts = 300

def random_float_generator(min_value, max_value, seed):
    random.seed(seed)
    random_number = random.uniform(0,1)
    value = min_value + (max_value-min_value)*random_number
    return value

def create_random_material(number_of_materials, seed):
    random.seed(seed)
    material = random.randint(0, number_of_materials-1)
    return material

def write_excel_global_scenario(df_parts,df_sites,df_material, df_general_parameters, scenario, folder, case_name):
    df_parts_global = df_parts[df_parts['origin'].isin(scenario)]
    df_sites_global = df_sites[df_sites['location'].isin(scenario)]
    df_material_global = df_material
    os.chdir(folder)
    filename = case_name + ".xlsx"
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    df_parts_global.to_excel(writer, sheet_name='Parts')
    df_sites_global.to_excel(writer, sheet_name='Site')
    df_material_global.to_excel(writer, sheet_name='Materials')
    df_transport_matrix.to_excel(writer, sheet_name='Transport')
    df_general_parameters.to_excel(writer, sheet_name='Parameters')
    
    writer.save()
  
def create_distribution_parts(roulette_matrix, number_of_parts, seed):
    distribution_list_distination = []
    distribution_list_origin = []
    
    for i in range(number_of_parts):
        random.seed(seed+i)
        random_number = random.random()
        for row in roulette_matrix_destination_parts.iterrows():
            if random_number >= row[1]["Min"] and random_number <=row[1]["Max"]:
                distribution_list_distination.append(row[1]["Region"])
        random.seed(seed+i+566)
        random_number = random.random()
        for row in roulette_matrix_origin_parts.iterrows():
            if random_number >= row[1]["Min"] and random_number <=row[1]["Max"]:
                distribution_list_origin.append(row[1]["Region"])
        
    return distribution_list_distination, distribution_list_origin

def create_distribution_parts_2(roulette_matrix, number_of_parts, number_of_parts_per_site, seed):
    distribution_list_distination = []
    distribution_list_origin = []
    
    for i in range(number_of_parts):
        random.seed(seed+i)
        random_number = random.random()
    
        for row in roulette_matrix_destination_parts.iterrows():
            if random_number >= row[1]["Min"] and random_number <=row[1]["Max"]:
                distribution_list_distination.append(row[1]["Region"])
        
        site_id = int(np.floor(i / number_of_parts_per_site))
        distribution_list_origin.append(roulette_matrix_origin_parts.iloc[site_id]["Region"])
    return distribution_list_distination, distribution_list_origin

def create_part_prices(part_volume, part_height, origin, destination, df_transport, df_sites, parameters):
    margin = 0.05
    duration = (part_volume * float(parameters["max_speed_xy"])/float(parameters["resolution"]) + part_height*float(parameters["max_speed_z"])/float(parameters["resolution"]))/3600.0
    transport_duration = float(df_transport[df_transport["Destination"]==origin][destination])*24
    tau = float(df_sites[df_sites["destination"]==origin]["production_cost_factor"])
    production_costs = duration * tau
    sigma = df_sites.iloc[0]["setup_cost_factor"]
    setup_time = df_sites.iloc[0]["setup_time_batching"]
    costs = production_costs
    #transport_costs = float((costs / (1-margin) * float(parameters["psi"]) + float(parameters["omega"]) *transport_duration)*1.2)
    #transport_costs = transport_costs 
    price = float(costs / (1-margin))
    return price    

def create_parts(list_destination_parts, seed):
    part_list = pd.DataFrame()
    df_parameter_list = input_data[input_data["Sheet"]=="Parts"]
    i=0

    for j in range(len(list_destination_parts)):
        i +=1
        dict_part = {"destination":list_destination_parts[j]}
        dict_part["origin"] = list_origin_parts[j]
        dict_part["material"] = create_random_material(number_of_materials, seed+i)

        for row in df_parameter_list.iterrows():
            i += 1
            value = random_float_generator(row[1]["Min"],row[1]["Max"],seed+i)
            key = row[1]["Parameter"]
            dict_part[key] = value
        
        if dict_part["length"]>dict_part["width"]:
            length = dict_part["length"]
            width = dict_part["width"]
        else:
            length = dict_part["width"]
            width = dict_part["length"]
            
        dict_part.update({"width": width})
        dict_part.update({"length": length})
        
        
        height = dict_part["height"]

        volume = height*length*width
        origin = dict_part["origin"]
        destination = dict_part["destination"]
        dict_part["price"] = create_part_prices(volume, height, origin, destination, df_transport_matrix, df_sites_output, df_parameters.iloc[0])
        part_list = part_list.append(dict_part, ignore_index=True)
    return part_list

roulette_matrix_destination_parts = input_data[input_data["Sheet"]=="Distribution of Parts"][["Parameter", "Min", "Max"]].rename(columns={"Parameter":"Region"})
roulette_matrix_origin_parts = input_data[input_data["Sheet"]=="Number of Machines"][["Parameter", "Min", "Max"]].rename(columns={"Parameter":"Region"})
number_of_materials = int(input_data[input_data["Parameter"]=="number_of_materials"]["Value"])

list_destination_parts, list_origin_parts = create_distribution_parts_2(roulette_matrix_destination_parts, number_of_parts, 20, 999)

list_sites = []
df_sites_input = input_data[input_data["Sheet"]=="Number of Machines"][["Parameter", "Value"]]
df_factor_sites = input_data[input_data["Sheet"]=="Site"][["Parameter", "Value"]]
df_machines_sites = input_data[input_data["Sheet"]=="Machines"][["Parameter", "Value"]]
df_transport = input_data[input_data["Sheet"]=="Transport"][["Parameter", "Value"]]
df_parameters = input_data[input_data["Sheet"]=="General_Parameter"][["Parameter", "Value"]]
df_sites_output = pd.DataFrame()

i = 0
for row in df_sites_input.iterrows():
    destination = row[1]["Parameter"]
    number_of_machines = int(row[1]["Value"])
    
    site_dict = {"destination":destination,
                 "number_of_machines":number_of_machines,
                "side_id":i}
    
    for cost_factor_row in df_factor_sites.iterrows():
        key = cost_factor_row[1]["Parameter"]
        value = cost_factor_row[1]["Value"]
        site_dict[key] = value
    
    for machine_parameter in df_machines_sites.iterrows():
        key = machine_parameter[1]["Parameter"]
        value = machine_parameter[1]["Value"]
        site_dict[key] = value
        
        
    df_sites_output = df_sites_output.append(site_dict, ignore_index=True)
    i+=1
    
df_sites_output["site_id"] = df_sites_output["site_id"].astype(int)
df_sites_output["number_of_machines"] = df_sites_output["number_of_machines"].astype(int)

df_materials = pd.DataFrame()
for i in range(number_of_materials):
    dict_material = {
        "index": i}
    df_materials = df_materials.append(dict_material, ignore_index=True)
df_materials["index"] = df_materials["index"].astype(int)

scenario_1 = ["A"]
scenario_2 = ["A", "B"]
scenario_3 = ["A", "B", "C"]
scenario_4 = ["A", "B", "C", "D"]
scenario_5 = ["A", "B", "C", "D", "E"]
scenario_6 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
scenario_7 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]

#parts_per_site = [20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20]

scenarios = [ scenario_1, scenario_2, scenario_3, scenario_4, scenario_5, scenario_6, scenario_7]
number_of_scenarios = len(scenarios)

df_parameters = df_parameters.set_index("Parameter").transpose()

number_of_part_instances = 50
parent_folder = "C:/Users/dozehetner/Seafile/03_Research/02_Decentralized_Planning/06_Instances/01_Case_Study_IJPE_new_bundle_param_new_prices/01_Input_Data"
isExist = os.path.exists(parent_folder)

if not isExist:
  os.makedirs(parent_folder)
  print("The new directory is created!")

seed = 1
for k in range(number_of_part_instances):
    df_parts = create_parts(list_destination_parts, seed+k*1000)
    for j in range(number_of_scenarios):
        case_name = "S"+str(j+1)+"I"+str(k+1).zfill(2)
        path = parent_folder
        scenario = scenarios[j]
        write_excel_global_scenario(df_parts,df_sites_output,df_materials, df_parameters, scenario, path, case_name)