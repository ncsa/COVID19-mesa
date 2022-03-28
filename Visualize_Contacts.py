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
import psutil

def smooth_average(values, scale):
    new_list = []
    for index, value in enumerate(values):
        average = 0
        count = 0
        for index_2 in range(index-(scale*96)+1, index+1, 1):
            if (index_2 >= 0):
                average += values[index_2]
                count += 1

        average = average / count
        new_list.append(average)
    return new_list





general_features = ["Generally_Infected"]
mortality_features = []
variant_features = []
vaccine_features = []


#This dictionary contains all the features of interest. To add more features as a seperate image,
# create another list and add it in this dictionary
all_features = {"general_features": general_features,"mortality_features": mortality_features, "variant_features": variant_features, "vaccine_features": vaccine_features}

input_directory_list = [] #Directories of the output files
output_filenames_list = [] #List of output file names TODO: Change the names according to what we are trying to find.
input_filenames_list = [] #List of input file names from the directories

for argument in sys.argv[1:]:
    input_directory_list.append(argument)

for directory in input_directory_list:
    file_list = glob.glob(f"{directory}/*.csv")
    for file in file_list:
        if not("agent" in file):
            input_filenames_list.append(file)

for file in input_filenames_list:
    out_file = file.replace(".csv", ".png")
    output_filenames_list.append(out_file)


data_list = {}
average_list = {}
for file in input_filenames_list:
    thing = file.replace("scenarios/Contact_Identifier/Results\Contact_Test-model_","")
    thing = thing.replace(".csv", "")
    thing = thing.replace("(", "")
    thing = thing.replace(")", "")
    data = tuple(map(int, thing.split(', ')))
    population = data [0]
    area = data[1]*data[2]
    data_list[file] = (population, area)

np.seterr(all="ignore")

def calculate_averages(file, input_dict, key):
    #Calculate the averages for daily and unique contacts, return both averages.
    df = pd.read_csv(file)
    daily_contact_average = 0
    alltime_contact_average = 0
    for step in df["Step"].unique():
        values = df["Rt"][df["Step"] == step]
        daily_contact_average += values.mean()
        values =  df["Total_Contact"][df["Step"] == step]
        alltime_contact_average += values.mean()
    daily_contact_average = daily_contact_average/len(df["Step"].unique())
    alltime_contact_average = alltime_contact_average/len(df["Step"].unique())
    return daily_contact_average, df["Total_Contact"][df["Step"] == df["Step"].max()].mean()




def visualize(index, in_file):#Visualize feature per file of interest.\
    mem = psutil.virtual_memory()
    initial_mem = mem.available
    print("Memory_Available: ", initial_mem/(1024 * 1024) , "MB")

    df0 = pd.read_csv(in_file)  #File is the same across all images.
    df0["Step"] = df0["Step"] / 96

    for image_name, feature_list in all_features.items():
        #Initializing plot
        plt.figure(figsize = (200.7, 100.27))
        plt.ticklabel_format(style='plain', axis='y')
        fig, ax = plt.subplots()
        legends_list = []
        for index_2, feature in enumerate(feature_list):
            #TODO create a list of dataframes
            df = pd.DataFrame()
            df["Step"] = df0["Step"]
            df[feature] = df0[feature]#*100

            xmin = 0
            xmax = df["Step"].max()
            ymin = 0

            avg = []
            low_ci_95 = []
            high_ci_95 = []
            for step in df["Step"].unique():
                values = df[feature][df["Step"] == step]
                f_mean = values.mean()
                lci95, hci95 = sps.t.interval(0.95, len(values), loc=f_mean, scale=sps.sem(values))
                avg.append(f_mean)
                low_ci_95.append(lci95)
                high_ci_95.append(hci95)
            #For normal representation, change smoothness to 1
            smoothness = 1
            smooth_mean = smooth_average(avg,smoothness)
            df_stats = pd.DataFrame()
            df_stats["Step"] = df["Step"].unique()
            df_stats["mean"] = avg
            df_stats["lci95"] = low_ci_95
            df_stats["hci95"] = high_ci_95
            df_stats["smooth_average"] = smooth_mean
            cur_color = "blue"
            # cur_color = ((index_2+1)/len(features)), 0.5*((index_2+1)/len(features)), 1-((index_2+1)/len(features))
            if (feature == "Vaccinated"):
                cur_color = "lime"
            elif (feature == "Generally_Infected"):
                cur_color = "red"
            elif (feature == "Susceptible"):
                cur_color = "blue"
            elif (feature == "Deceased"):
                cur_color = "black"
            elif (feature == "AsympDetected"):
                cur_color = "brown"
            elif (feature == "SymptQuarantined"):
                cur_color = "yellow"
            elif (feature == "Recovered"):
                cur_color = "green"
            elif (feature == "Exposed"):
                cur_color = "purple"
            elif (feature == "Fully_Vaccinated"):
                cur_color = "gold"

            ax.plot(df_stats["Step"], df_stats["smooth_average"], color=cur_color, label = feature, linewidth = 1)
            ax.fill_between(df_stats["Step"], df_stats["lci95"], df_stats["hci95"], color=cur_color, alpha=.1)
            event_times = []
            for vline in event_times:
                ax.vlines(3, 0, ymax, colors='gray', linestyle="--")
            ax.set_xlim([xmin, xmax])
            ax.set_xlabel("Days")
            ax.set_ylabel("Number of Agents")
            legend = mpatches.Patch(color=cur_color)
            legends_list.append(legend)

        mem = psutil.virtual_memory()
        print("Memory_Available: ", mem.available / (1024 * 1024), "MB")
        ax.set_title(image_name)
        plt.axis('tight')
        plt.legend(legends_list, feature_list, bbox_to_anchor=(0.90, 1.1), loc="upper left", borderaxespad=0, fontsize='xx-small')
        output = output_filenames_list[index].replace(".png", image_name + ".png")
        plt.savefig(output, dpi=700)
        plt.close()




data_1 = {}
data_2 = {}
print(data_list)
for file, key in data_list.items():
    print(file, key)
    daily, total = calculate_averages(file, data, key)
    data_1[key] = daily
    data_2[key] = total


by_area = {}
by_pop  = {}

data_per_key_area = {}
data_per_key_pop = {}

fig, ax = plt.subplots()
space_list = [(25*25), (50*50), (75*75), (100*100), (125*125), (150*150)]
space_list_tuples = [(25,25), (50,50), (75,75), (100,100), (125,125), (150,150)]
population_list = [100,150,200,250,300]

legends_list = []
color_index = 0
color_list  = ["red", "green", "blue", "black", "gold", "orange", "lime"]
for index, population in enumerate(population_list):
    axis_1 = []
    values_1 = []
    by_area = {}
    for key, value in data_1.items():
        if key[0] == population:
            by_area[key[1]] = value
    by_area_listed = sorted(by_area)
    for key in by_area_listed:
        values_1.append(by_area[key])
        axis_1.append(key)
    color_index = (color_index+1)%(len(color_list)-1)
    cur_color = color_list[color_index]
    ax.plot(axis_1, values_1, color=cur_color, label=f"{population}", linewidth=1)
    legend = mpatches.Patch(color=cur_color)
    legends_list.append(legend)


ax.set_xlabel("Area")
ax.set_ylabel("Average_Contact")
ax.set_title("Daily Average Contact by Area")
plt.axis('tight')
plt.legend(legends_list, population_list, bbox_to_anchor=(0.90, 1.1), loc="upper left", borderaxespad=0, fontsize='xx-small')
plt.savefig("scenarios/Contact_Identifier/Results/Rt.png", dpi=700)
plt.close()

fig, ax = plt.subplots()
color_index= 0
for index, area in enumerate(space_list):
    axis_1 = []
    values_1 = []
    by_pop = {}
    for key, value in data_1.items():
        if key[1] == area:
            by_pop[key[0]] = value
        print(key[0], by_pop)
    #PLOT AND SAVE
    by_pop_sorted = sorted(by_pop)
    for key in by_pop_sorted:
        values_1.append(by_pop[key])
        axis_1.append(key)

    print(axis_1, values_1)
    color_index = (color_index + 1) % (len(color_list) - 1)
    cur_color = color_list[color_index]
    ax.plot(axis_1, values_1, color=cur_color, label=f"{population}", linewidth=1)
    legend = mpatches.Patch(color=cur_color)
    legends_list.append(legend)

print("Made it here")
ax.set_xlabel("Populations")
ax.set_ylabel("Average_Contact")
ax.set_title("Daily Average Contact by Population")
plt.axis('tight')
plt.legend(legends_list, space_list_tuples, bbox_to_anchor=(0.90, 1.1), loc="upper left", borderaxespad=0, fontsize='xx-small')
plt.savefig("scenarios/Contact_Identifier/Results/RTpop.png", dpi=700)
plt.close()
