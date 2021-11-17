# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu
# A simple tunable model for COVID-19 response
import matplotlib.pyplot as plot
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
import scipy.stats as stats

plot.rcParams['agg.path.chunksize'] = 10000

features = ["Data_Time","Step_Time"]

def linear_model(x, slope, intercept):
    new_list = []
    for element in x:
        new_list.append(element*slope+intercept)
    return new_list


input_directory_list = []
output_filenames_list = []
input_filenames_list = []
#
# for argument in sys.argv[1:]:
#     input_directory_list.append(argument)
# agent_count_list = []
agent_count_list = [100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000]
agent_count_list_2 = [100,200,300,400,500,600,700,800,900,1000]
iteration_list = iteration_list = [1,2,3,4]

"""No Backtracking Files"""
No_backtracking_data_storage_file_1 = "outcomes/Debugging/Test_Runtime/Total_Running_Times_0_10_No_backtracking.csv"
No_backtracking_df_1 = pd.read_csv(No_backtracking_data_storage_file_1)
# data_storage_file_2 = "outcomes/Debugging/Test_Runtime/Total_Running_Times_10_21_No_backtracking.csv"
# backtracking_df_2 = pd.read_csv(data_storage_file_2)
# frames = [No_backtracking_df_1, backtracking_df_2]


frames = [No_backtracking_df_1]
no_backtracking_data_storage_df = pd.concat(frames, ignore_index = True)

""""Backtracking Files"""
backtracking_data_storage_file_1 = "outcomes/Debugging/Test_Runtime/Total_Running_Times_0_10_backtracking.csv"
backtracking_df_1 = pd.read_csv(backtracking_data_storage_file_1)
# data_storage_file_2 = "outcomes/Debugging/Test_Runtime/Data_Storage_Times.csv"
# backtracking_df_2 = pd.read_csv(data_storage_file_2)
nb_frames = [backtracking_df_1]
backtracking_data_storage_df = pd.concat(nb_frames)


All_No_Backtracking_Data_Storage_Times = []
All_Backtracking_Data_Storage_Times = []

for iteration in iteration_list:
    No_Backtracking_Data_Storage_Times = []
    Backtracking_Data_Storage_Times = []

    for index in range(len(np.array(no_backtracking_data_storage_df))):
        time = no_backtracking_data_storage_df["Iteration"+str(iteration)][index]
        No_Backtracking_Data_Storage_Times.append(time)

    for index in range(len(np.array(backtracking_data_storage_df))):
        time = backtracking_data_storage_df["Iteration"+str(iteration)][index]
        Backtracking_Data_Storage_Times.append(time)

    All_No_Backtracking_Data_Storage_Times.append(No_Backtracking_Data_Storage_Times)
    All_Backtracking_Data_Storage_Times.append(Backtracking_Data_Storage_Times)


for iteration in iteration_list:
    #Initialize the plot
    namesuf = str(iteration)
    plot.figure(figsize=(200.7, 100.27))
    plot.ticklabel_format(style='plain', axis='y')
    fig, ax = plot.subplots()




    ax.plot(agent_count_list_2, All_No_Backtracking_Data_Storage_Times[iteration-1], color="red", label=("No_Backtracking_Storage_Times"), linewidth=2)
    ax.plot(agent_count_list_2, All_Backtracking_Data_Storage_Times[iteration-1], color="blue", label=("Backtracking_Storage_Times"), linewidth=2)
    slope, intercept, r_value, p_value, std_err =stats.linregress(agent_count_list_2, All_No_Backtracking_Data_Storage_Times[iteration-1])
    print("Slope and intercept for No Backtracking respectively is :", slope, ":::", intercept)
    model_runtime = linear_model(agent_count_list_2,slope,intercept)
    ax.plot(agent_count_list_2, model_runtime, label = "BestRuntimeFit for No Backtracking", color = "orange", linewidth=1)
    slope, intercept, r_value, p_value, std_err = stats.linregress(agent_count_list_2, All_Backtracking_Data_Storage_Times[iteration - 1])
    print("Slope and intercept for Backtracking respectively is :", slope, ":::", intercept)
    model_runtime = linear_model(agent_count_list_2, slope, intercept)
    ax.plot(agent_count_list_2, model_runtime, label="BestRuntimeFit for Backtracking",  color = "purple", linewidth=1)



    legends_list = []
    legend1 = mpatches.Patch(color="red")
    legends_list.append(legend1)
    legend2 = mpatches.Patch(color="blue")
    legends_list.append(legend2)
    plot.axis('tight')

    ax.set_xlabel("Agent_Count")
    ax.set_ylabel("Time(s)")

    names = ["Total_Running_Times_No_backtracking", "Total_Running_Times_backtracking"]
    plot.legend(legends_list, names, bbox_to_anchor=(1.05, 0.8), loc="upper right", borderaxespad=0, fontsize='xx-small')
    ax.set_title(f"Total Running Times for {iteration} iterations")
    out_file = f"visualizations/Debugging/Test_Runtime/Total_Running_Times_{iteration}.png"
    print(out_file)
    plot.savefig(out_file, dpi=700)
    plot.close()




# """Average_Calculation:"""
#
# backtracking_input_filenames_list = []
#
# for directory in input_directory_list:
#     for count in agent_count_list:
#         print(f"{directory}/backtracking{str(count)}.csv")
#         file_list = glob.glob(f"{directory}/backtracking{str(count)}.csv")
#         for file in file_list:
#             backtracking_input_filenames_list.append(file)
#
# no_backtracking_input_filenames_list = []
# for directory in input_directory_list:
#     for count in agent_count_list:
#         print(f"{directory}/backtracking{str(count)}.csv")
#         file_list = glob.glob(f"{directory}/No_backtracking{str(count)}.csv")
#         for file in file_list:
#             no_backtracking_input_filenames_list.append(file)
#
# total_backtracking = [[] for _ in range(3)]
# total_no_backtracking = [[] for _ in range(3)]
# average_backtracking = [[] for _ in range(3)]
# average_no_backtracking = [[] for _ in range(3)]
# print(total_backtracking[0], total_no_backtracking, average_backtracking, average_no_backtracking)
#
# print("Backtracking Files: ")
# for item in backtracking_input_filenames_list:
#     print(item)
#
# print("Non backtracking Files: ")
# for item in no_backtracking_input_filenames_list:
#     print(item)
#
# """0 -> Data_Time, 1 -> Step_Time, 2 -> Total_Time """
# for iteration in range(3):
#     """Calculating Backtracking Totals"""
#     backtracking_average_list = []
#     backtracking_total_list = []
#     for index, in_file in enumerate(backtracking_input_filenames_list):
#         df = pd.read_csv(in_file)
#         print(iteration, index+1, len(backtracking_input_filenames_list))
#         total = 0
#         for idx in df["Step"].unique():
#             if (iteration == 0):#Data
#                 values = df[features[0]][df["Step"] == idx]
#                 avg = values.mean()
#                 total += avg
#             elif (iteration == 1):#Step
#                 values = df[features[1]][df["Step"] == idx]
#                 avg = values.mean()
#                 total += avg
#             elif (iteration == 2): #Total
#                 values = df[features[1]][df["Step"] == idx] + df[features[0]][df["Step"] == idx]
#                 avg = values.mean()
#                 total += avg
#         total_backtracking[iteration].append(total)
#         average = total/len(df[features[0]])
#         average_backtracking[iteration].append(average)
#
#
#
#     """Calculating Non-Backtracking Totals"""
#     no_backtracking_total_list = []
#     no_backtracking_average_list = []
#     for index, in_file in enumerate(no_backtracking_input_filenames_list):
#         df = pd.read_csv(in_file)
#         print(iteration, index+1, len(no_backtracking_input_filenames_list))
#         total = 0
#         for idx in df["Step"].unique():
#             if (iteration == 0):  # Data
#                 values = df[features[0]][df["Step"] == idx]
#                 avg = values.mean()
#                 total += avg
#             elif (iteration == 1):  # Step
#                 values = df[features[1]][df["Step"] == idx]
#                 avg = values.mean()
#                 total += avg
#             elif (iteration == 2):  # Total
#                 values = df[features[1]][df["Step"] == idx] + df[features[0]][df["Step"] == idx]
#                 avg = values.mean()
#                 total += avg
#
#         total_no_backtracking[iteration].append(total)
#         average = total / len(df[features[0]])
#         average_no_backtracking[iteration].append(average)
#
#
#
# for avg in range(2):
#     for iteration in range(3):
#         #Initialize the plot
#         namepref = ""
#         namesuf = ""
#         plot.figure(figsize=(200.7, 100.27))
#         plot.ticklabel_format(style='plain', axis='y')
#         fig, ax = plot.subplots()
#         if(iteration == 0):
#             namepref = "Data_Time"
#         if (iteration == 1):
#             namepref = "Step_Time"
#         if (iteration == 2):
#             namepref = "Total_Time"
#
#         if avg:
#             namesuf = "Average"
#             ax.plot(agent_count_list, average_backtracking[iteration], color="red", label=(namepref + " " + "Backtracking Average"), linewidth=1)
#             ax.plot(agent_count_list, average_no_backtracking[iteration], color="blue", label=(namepref +" " + "No Backtracking Average"),
#                     linewidth=1)
#         else:
#             namesuf = "Total"
#             ax.plot(agent_count_list, total_backtracking[iteration], color="red", label=(namepref +" " + "Backtracking Total"), linewidth=1)
#             ax.plot(agent_count_list, total_no_backtracking[iteration], color="blue", label=(namepref +" " + "No Backtracking Total"),
#                     linewidth=1)
#
#         legends_list = []
#         legend1 = mpatches.Patch(color="red")
#         legends_list.append(legend1)
#         legend2 = mpatches.Patch(color="blue")
#         legends_list.append(legend2)
#         plot.axis('tight')
#         names = [namepref+ " " + "Backtracking" + " " + namesuf, namepref+ " " +  "No Backtracking" + " " + namesuf]
#         plot.legend(legends_list, names, bbox_to_anchor=(1.05, 0.8), loc="upper right", borderaxespad=0,
#                     fontsize='xx-small')
#         ax.set_title(namepref+ " "+ namesuf + "s")
#         file = no_backtracking_input_filenames_list[0]
#         out_file = file.replace("outcomes/", "visualizations/")
#         out_file = file.replace("No_backtracking100", "")
#         out_file = out_file.replace(".csv", namepref+ "_"+ namesuf + "s" + ".png")
#         print(out_file)
#         plot.savefig(out_file, dpi=700)
#         plot.close()













#
# for directory in input_directory_list:
#     file_list = glob.glob(f"{directory}/*.csv")
#     for file in file_list:
#         input_filenames_list.append(file)
#
# for file in input_filenames_list:
#     out_file = file.replace("outcomes/", "visualizations/")
#     out_file = out_file.replace(".csv", "-data_time.png")
#     output_filenames_list.append(out_file)
#
# print(input_directory_list)
# print(input_filenames_list)
# print(output_filenames_list)
#
# np.seterr(all="ignore")
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
