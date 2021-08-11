# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu
# A simple tunable model for COVID-19 response
import matplotlib.pyplot as plt
import scipy.stats as sps
import seaborn as sns
import pandas as pd
import numpy as np
from covidmodel import CovidModel
import matplotlib.patches as mpatches
import sys
import multiprocessing
import glob
import os


features = ["Step_Time"]

input_directory_list = []
output_filenames_list = []
input_filenames_list = []

for argument in sys.argv[1:]:
    input_directory_list.append(argument)

for directory in input_directory_list:
    file_list = glob.glob(f"{directory}/*.csv")
    for file in file_list:
        input_filenames_list.append(file)

for file in input_filenames_list:
    out_file = file.replace("outcomes/", "visualizations/")
    out_file = out_file.replace(".csv", "-steptime.png")
    output_filenames_list.append(out_file)

print(input_directory_list)
print(input_filenames_list)
print(output_filenames_list)

np.seterr(all="ignore")
#features will be a list of features requested on the graph

def visualize(index, in_file):
    plt.figure(figsize = (200.7, 100.27))
    plt.ticklabel_format(style='plain', axis='y')
    df0 = pd.read_csv(in_file)
    df0["Step"] = df0["Step"]/96

    df_list = []
    xmin_list = []
    xmax_list = []
    ymin_list = []
    ymin = 0
    fig, ax = plt.subplots()
    average_lists = []

    df_stats_list = []
    legends_list = []
    labels_list = []
    index_list = [range(len(features))]
    for idx,feature in enumerate(features):
        #TODO create a list of dataframes
        df = pd.DataFrame()
        df["Step"] = df0["Step"]
        df[feature] = df0[feature]#*100
        xmin = 0
        xmax = df["Step"].max()
        ymax = df[feature].max()
        avg = []
        low_ci_95 = []
        high_ci_95 = []
        low_ci_99 = []
        high_ci_99 = []
        print(f"Computing confidence intervals... {feature}")
        for step in df["Step"].unique():
            values = df[feature][df["Step"] == step]
            f_mean = values.mean()
            lci95, hci95 = sps.t.interval(0.95, len(values), loc=f_mean, scale=sps.sem(values))
            lci99, hci99 = sps.t.interval(0.99, len(values), loc=f_mean, scale=sps.sem(values))
            avg.append(f_mean)
            low_ci_95.append(lci95)
            high_ci_95.append(hci95)
            low_ci_99.append(lci99)
            high_ci_99.append(hci99)

        df_stats = pd.DataFrame()
        df_stats["Step"] = df["Step"].unique()
        df_stats["mean"] = avg
        df_stats["lci95"] = low_ci_95
        df_stats["hci95"] = high_ci_95
        df_stats["lci99"] = low_ci_99
        df_stats["hci99"] = high_ci_99
        cur_color = ((idx+1)/len(features)), 0.5*((idx+1)/len(features)), 1-((idx+1)/len(features))
        if (feature == "Vaccinated"):
            cur_color = "lime"
        elif (feature == "Generally_Infected"):
            cur_color = "red"
        elif (feature == "Susceptible"):
            cur_color = "blue"
        elif (feature == "Deceased"):
            cur_color = "black"
        elif (feature == "SymptQuarantined"):
            cur_color = "yellow"
        elif (feature == "Recovered"):
            cur_color = "skyblue"
        elif (feature == "Exposed"):
            cur_color = "purple"
        elif (feature == "Fully_Vaccinated"):
            cur_color = "olive"


        ax.plot(df_stats["Step"], df_stats["mean"], color=cur_color, label = feature, linewidth = 1)
        ax.fill_between(df_stats["Step"], df_stats["lci95"], df_stats["hci95"], color=cur_color, alpha=.1)
        ax.set_xlim([xmin, xmax])
        ax.set_ylim([ymin, ymax])
        ax.set_xlabel("Days")
        ax.set_ylabel("Pop. Fraction")
        legend = mpatches.Patch(color=cur_color)
        legends_list.append(legend)


    plt.axis('tight')
    plt.legend(legends_list, features, bbox_to_anchor=(1.05, 0.8), loc="upper right", borderaxespad=0, fontsize='xx-small')
    plt.savefig(output_filenames_list[index], dpi=700)
    plt.close()

if __name__ == '__main__':
    processes = []
    for index, in_file in enumerate(input_filenames_list):
        p = multiprocessing.Process(target=visualize, args=[index, in_file])
        p.start()
        processes.append(p)

    for process in processes:
        process.join()
