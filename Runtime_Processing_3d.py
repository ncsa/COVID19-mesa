# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu
# A simple tunable model for COVID-19 response
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d.axes3d import get_test_data
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
import time
import pickle



plot.rcParams['agg.path.chunksize'] = 10000

features = ["Data_Time","Step_Time"]

input_directory_list = []
output_filenames_list = []
input_filenames_list = []

for argument in sys.argv[1:]:
    input_directory_list.append(argument)
# agent_count_list = []
agent_count_list = [100,200,300,400,500,600,700,800,900,1000,1100,1200] #X-Coordinate
iteration_list = [1,2,3,4,5,6,7,8,9,10,11,12] #Y-Coordinate
#Z-Coordinate = ? (12,12) matrix




"""Average_Calculation:"""

backtracking_input_filenames_list = []

for directory in input_directory_list:
    for count in agent_count_list:
        for iteration in iteration_list:
            print(f"{directory}/backtracking_{str(count)}_{iteration}.csv")
            if (len(glob.glob(f"{directory}/backtracking_{str(count)}*.csv")) < 12):
                continue
            file_list = glob.glob(f"{directory}/backtracking_{str(count)}_{iteration}.csv")
            for file in file_list:
                backtracking_input_filenames_list.append(file)

no_backtracking_input_filenames_list = []
for directory in input_directory_list:
    for count in agent_count_list:
        for iteration in iteration_list:
            print(f"{directory}/backtracking_{str(count)}_{iteration}.csv")
            if(len(glob.glob(f"{directory}/No_backtracking_{str(count)}*.csv")) < 12):
                continue
            file_list = glob.glob(f"{directory}/No_backtracking_{str(count)}_{iteration}.csv")
            for file in file_list:
                no_backtracking_input_filenames_list.append(file)

total_backtracking = [[] for _ in range(3)]
total_no_backtracking = [[] for _ in range(3)]
average_backtracking = [[] for _ in range(3)]
average_no_backtracking = [[] for _ in range(3)]

print("Backtracking Files: ")
for item in backtracking_input_filenames_list:
    print(item)

print("Non backtracking Files: ")
for item in no_backtracking_input_filenames_list:
    print(item)

"""0 -> Data_Time, 1 -> Step_Time, 2 -> Total_Time """
for iteration in range(3):

    """Calculating Backtracking Totals"""
    backtracking_average_list = []
    backtracking_total_list = []
    for index, in_file in enumerate(backtracking_input_filenames_list):
        df = pd.read_csv(in_file)
        print(iteration, index+1, len(backtracking_input_filenames_list))
        total = 0
        for idx in df["Step"].unique():
            if (iteration == 0):#Data
                values = df[features[0]][df["Step"] == idx]
                avg = values.mean()
                total += avg
            elif (iteration == 1):#Step
                values = df[features[1]][df["Step"] == idx]
                avg = values.mean()
                total += avg
            elif (iteration == 2): #Total
                values = df[features[1]][df["Step"] == idx] + df[features[0]][df["Step"] == idx]
                avg = values.mean()
                total += avg
        total_backtracking[iteration].append(total)
        average = total/len(df[features[0]])
        average_backtracking[iteration].append(average)



    """Calculating Non-Backtracking Totals"""
    no_backtracking_total_list = []
    no_backtracking_average_list = []
    for index, in_file in enumerate(no_backtracking_input_filenames_list):
        df = pd.read_csv(in_file)
        print(iteration, index+1, len(no_backtracking_input_filenames_list))
        total = 0
        for idx in df["Step"].unique():
            if (iteration == 0):  # Data
                values = df[features[0]][df["Step"] == idx]
                avg = values.mean()
                total += avg
            elif (iteration == 1):  # Step
                values = df[features[1]][df["Step"] == idx]
                avg = values.mean()
                total += avg
            elif (iteration == 2):  # Total
                values = df[features[1]][df["Step"] == idx] + df[features[0]][df["Step"] == idx]
                avg = values.mean()
                total += avg

        total_no_backtracking[iteration].append(total)
        average = total / len(df[features[0]])
        average_no_backtracking[iteration].append(average)

data_name_list =["Iteration" + str(name) for name in iteration_list]

for index in range(3):
    namepref = ""
    if (index == 0):
        namepref = "Data_Time"
    if (index == 1):
        namepref = "Step_Time"
    if (index == 2):
        namepref = "Total_Time"

    total_backtracking_df = pd.DataFrame(np.array(total_backtracking[index]).reshape(int(len(total_backtracking[index])/12),12), columns=data_name_list)
    total_backtracking_df.to_csv(f"outcomes/Debugging/Test_Runtime/total_backtracking_df_{namepref}.csv")
    total_no_backtracking_df = pd.DataFrame(np.array(total_no_backtracking[index]).reshape(int(len(total_no_backtracking[index])/12), 12), columns=data_name_list)
    total_no_backtracking_df.to_csv(f"outcomes/Debugging/Test_Runtime/total_no_backtracking_df_{namepref}.csv")
    average_backtracking_df = pd.DataFrame(np.array(average_backtracking[index]).reshape(int(len(average_backtracking[index])/12), 12), columns=data_name_list)
    average_backtracking_df.to_csv(f"outcomes/Debugging/Test_Runtime/average_backtracking_df_{namepref}.csv")
    average_no_backtracking_df = pd.DataFrame(np.array(average_no_backtracking[index]).reshape(int(len(average_no_backtracking[index])/12), 12), columns=data_name_list)
    average_no_backtracking_df.to_csv(f"outcomes/Debugging/Test_Runtime/average_no_backtracking_df_{namepref}.csv")

print("Processed all data")


for avg in range(2):
    for iteration in range(3):
        #Initialize the plot
        namepref = ""
        namesuf = ""

        fig = plot.figure()
        ax = fig.add_subplot(111, projection='3d')






        if(iteration == 0):
            namepref = "Data_Time"
        if (iteration == 1):
            namepref = "Step_Time"
        if (iteration == 2):
            namepref = "Total_Time"



        x, y = np.meshgrid(agent_count_list, iteration_list)
        if avg:
            namesuf = "Average"
            ax.plot_surface(x, y, np.array(average_backtracking[iteration]).reshape(int(len(average_backtracking[iteration])/12),12), color="red", label=(namepref + " " + "Backtracking Average"), linewidth=1)
            ax.plot_surface(x, y, np.array(average_no_backtracking[iteration]).reshape(int(len(average_no_backtracking[iteration])/12),12), color="blue", label=(namepref + " " + "No_Backtracking Average"), linewidth=1)
        else:
            namesuf = "Total"
            ax.plot_surface(x, y, np.array(total_backtracking[iteration]).reshape(int(len(total_backtracking[iteration])/12),12), color="red", label=(namepref + " " + "Backtracking Total"), linewidth=1)
            ax.plot_surface(x, y, np.array(total_no_backtracking[iteration]).reshape(int(len(total_no_backtracking[iteration])/12),12), color="blue", label=(namepref + " " + "No_Backtracking Total"), linewidth=1)


        plot.show()
        legends_list = []
        legend1 = mpatches.Patch(color="red")
        legends_list.append(legend1)
        legend2 = mpatches.Patch(color="blue")
        legends_list.append(legend2)
        plot.axis('tight')
        names = [namepref+ " " + "Backtracking" + " " + namesuf, namepref+ " " +  "No Backtracking" + " " + namesuf]
        plot.legend(legends_list, names, bbox_to_anchor=(1.05, 0.8), loc="upper right", borderaxespad=0,
                    fontsize='xx-small')
        ax.set_title(namepref+ " "+ namesuf + "s")
        file = no_backtracking_input_filenames_list[0]
        out_file = file.replace("outcomes/*.csv", "visualizations/.csv")
        out_file = out_file.replace(".csv", namepref+ "_"+ namesuf + "s" + ".png")
        plot.savefig(out_file, dpi=700)
        plot.close()














for directory in input_directory_list:
    file_list = glob.glob(f"{directory}/*.csv")
    for file in file_list:
        input_filenames_list.append(file)

for file in input_filenames_list:
    out_file = file.replace("outcomes/", "visualizations/")
    out_file = out_file.replace(".csv", "-data_time.png")
    output_filenames_list.append(out_file)

print(input_directory_list)
print(input_filenames_list)
print(output_filenames_list)

np.seterr(all="ignore")
#features will be a list of features requested on the graph

#
# for index, in_file in enumerate(input_filenames_list):
#     plot.figure(figsize = (200.7, 100.27))
#     plot.ticklabel_format(style='plain', axis='y')
#     df0 = pd.read_csv(in_file)
#     df0["Step"] = df0["Step"]/96
#
#     df_list = []
#     xmin_list = []
#     xmax_list = []
#     ymin_list = []
#     ymax = 1.0
#     ymin = 0
#     fig, ax = plot.subplots()
#     average_lists = []
#
#     df_stats_list = []
#     legends_list = []
#     labels_list = []
#     index_list = [range(len(features))]
#     for idx,feature in enumerate(features):
#         #TODO create a list of dataframes
#         df = pd.DataFrame()
#         df["Step"] = df0["Step"]
#         df[feature] = df0[feature]#*100
#         xmin = 0
#         xmax = df["Step"].max()
#
#         avg = []
#         low_ci_95 = []
#         high_ci_95 = []
#         low_ci_99 = []
#         high_ci_99 = []
#         print(f"Computing confidence intervals... {feature}")
#         for step in df["Step"].unique():
#             values = df[feature][df["Step"] == step]
#             f_mean = values.mean()
#             lci95, hci95 = sps.t.interval(0.95, len(values), loc=f_mean, scale=sps.sem(values))
#             lci99, hci99 = sps.t.interval(0.99, len(values), loc=f_mean, scale=sps.sem(values))
#             avg.append(f_mean)
#             low_ci_95.append(lci95)
#             high_ci_95.append(hci95)
#             low_ci_99.append(lci99)
#             high_ci_99.append(hci99)
#
#         df_stats = pd.DataFrame()
#         df_stats["Step"] = df["Step"].unique()
#         df_stats["mean"] = avg
#         df_stats["lci95"] = low_ci_95
#         df_stats["hci95"] = high_ci_95
#         df_stats["lci99"] = low_ci_99
#         df_stats["hci99"] = high_ci_99
#         cur_color = ((idx+1)/len(features)), 0.5*((idx+1)/len(features)), 1-((idx+1)/len(features))
#         if (feature == "Vaccinated"):
#             cur_color = "lime"
#         elif (feature == "Generally_Infected"):
#             cur_color = "red"
#         elif (feature == "Susceptible"):
#             cur_color = "blue"
#         elif (feature == "Deceased"):
#             cur_color = "black"
#         elif (feature == "SymptQuarantined"):
#             cur_color = "yellow"
#         elif (feature == "Recovered"):
#             cur_color = "skyblue"
#         elif (feature == "Exposed"):
#             cur_color = "purple"
#         elif (feature == "Fully_Vaccinated"):
#             cur_color = "olive"
#
#
#         ax.plot(df_stats["Step"], df_stats["mean"], color=cur_color, label = feature, linewidth = 1)
#         ax.fill_between(df_stats["Step"], df_stats["lci95"], df_stats["hci95"], color=cur_color, alpha=.1)
#         ax.set_xlim([xmin, xmax])
#         ax.set_ylim([ymin, ymax])
#         ax.set_xlabel("Days")
#         ax.set_ylabel("Pop. Fraction")
#         legend = mpatches.Patch(color=cur_color)
#         legends_list.append(legend)
#
#
#     plot.axis('tight')
#     plot.legend(legends_list, features, bbox_to_anchor=(1.05, 0.8), loc="upper right", borderaxespad=0, fontsize='xx-small')
#     plot.savefig(output_filenames_list[index], dpi=700)
#     plot.close()
#
