# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 13:39:53 2022

@author: dozehetner
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

def plot_batch(df_parts):
    batches = df_parts["batch"].unique()
    
    figs = {}
    axs = {}
    for batch in batches:
        df_parts_batch_id = df_parts[df_parts["batch"]==batch] 
        print(batch)
        figs[batch], axs[batch] = plt.subplots()
        for row in df_parts_batch_id.iterrows():
            axs[batch].add_patch(Rectangle((row[1]["x_p"], row[1]["y_p"]), row[1]["length"], row[1]["width"], alpha=1.0, edgecolor="black", facecolor="white"))
        axs[batch].set(xlim=(0, 400), ylim=(0, 350))
        axs[batch].set_title(batch)
    plt.show()
    

