# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from batchrunner_local import BatchRunnerMP
from multiprocessing import freeze_support
from covidmodelcheckpoint import CovidModel
from covidmodelcheckpoint import CovidModel
from covidmodelcheckpoint import Stage
from covidmodelcheckpoint import AgeGroup
from covidmodelcheckpoint import SexGroup
from covidmodelcheckpoint import ValueGroup
from covidmodelcheckpoint import *
import pandas as pd
import json
import sys
import concurrent.futures
import multiprocessing
import os
import glob



directory_list = []
filenames_list = []
virus_data_file = open(str(sys.argv[1])) #First arguement must be the location of the variant data file


for argument in sys.argv[2:]:   # Every following arguement must be a folder containing scenario data
    directory_list.append(argument)

for directory in directory_list:    #Searches through the directories for scenario files
    file_list = glob.glob(f"{directory}/*.json")
    for file in file_list:
        filenames_list.append(file)

# Read JSON file
data_list = []
for file_params in filenames_list:      #Creates a data list based on the filenames
    with open(file_params) as f:
        data = json.load(f)
        data_list.append(data)

indexes = [range(len(data_list))]       #Creates a list of indeces associating an index to a data set.
virus_data = json.load(virus_data_file)

def runModelScenario(data, index, iterative_input): #Function that runs a specified scenario given parameters in data.

    print(f"Location: { data['location'] }")
    print(f"Description: { data['description'] }")
    print(f"Prepared by: { data['prepared-by'] }")
    print(f"Date: { data['date'] }")
    print("")
    print("Attempting to configure model from file...")
    # Observed distribution of mortality rate per age
    age_mortality = {
        AgeGroup.C80toXX: data["model"]["mortalities"]["age"]["80+"],
        AgeGroup.C70to79: data["model"]["mortalities"]["age"]["70-79"],
        AgeGroup.C60to69: data["model"]["mortalities"]["age"]["60-69"],
        AgeGroup.C50to59: data["model"]["mortalities"]["age"]["50-59"],
        AgeGroup.C40to49: data["model"]["mortalities"]["age"]["40-49"],
        AgeGroup.C30to39: data["model"]["mortalities"]["age"]["30-39"],
        AgeGroup.C20to29: data["model"]["mortalities"]["age"]["20-29"],
        AgeGroup.C10to19: data["model"]["mortalities"]["age"]["10-19"],
        AgeGroup.C00to09: data["model"]["mortalities"]["age"]["00-09"],
    }

    # Observed distribution of mortality rage per sex
    sex_mortality = {
        SexGroup.MALE: data["model"]["mortalities"]["sex"]["male"],
        SexGroup.FEMALE: data["model"]["mortalities"]["sex"]["female"],
    }

    age_distribution = {
        AgeGroup.C80toXX: data["model"]["distributions"]["age"]["80+"],
        AgeGroup.C70to79: data["model"]["distributions"]["age"]["70-79"],
        AgeGroup.C60to69: data["model"]["distributions"]["age"]["60-69"],
        AgeGroup.C50to59: data["model"]["distributions"]["age"]["50-59"],
        AgeGroup.C40to49: data["model"]["distributions"]["age"]["40-49"],
        AgeGroup.C30to39: data["model"]["distributions"]["age"]["30-39"],
        AgeGroup.C20to29: data["model"]["distributions"]["age"]["20-29"],
        AgeGroup.C10to19: data["model"]["distributions"]["age"]["10-19"],
        AgeGroup.C00to09: data["model"]["distributions"]["age"]["00-09"],
    }

    # Observed distribution of mortality rage per sex
    sex_distribution = {
        SexGroup.MALE: data["model"]["distributions"]["sex"]["male"],
        SexGroup.FEMALE: data["model"]["distributions"]["sex"]["female"],
    }

    # Value distribution per stage per interaction (micro vs macroeconomics)
    value_distibution = {
        ValueGroup.PRIVATE: {
            Stage.SUSCEPTIBLE: data["model"]["value"]["private"]["susceptible"],
            Stage.EXPOSED: data["model"]["value"]["private"]["exposed"],
            Stage.SYMPDETECTED: data["model"]["value"]["private"]["sympdetected"],
            Stage.ASYMPTOMATIC: data["model"]["value"]["private"]["asymptomatic"],
            Stage.ASYMPDETECTED: data["model"]["value"]["private"]["asympdetected"],
            Stage.SEVERE: data["model"]["value"]["private"]["severe"],
            Stage.RECOVERED: data["model"]["value"]["private"]["recovered"],
            Stage.DECEASED: data["model"]["value"]["private"]["deceased"]
        },
        ValueGroup.PUBLIC: {
            Stage.SUSCEPTIBLE: data["model"]["value"]["public"]["susceptible"],
            Stage.EXPOSED: data["model"]["value"]["public"]["exposed"],
            Stage.SYMPDETECTED: data["model"]["value"]["public"]["sympdetected"],
            Stage.ASYMPTOMATIC: data["model"]["value"]["public"]["asymptomatic"],
            Stage.ASYMPDETECTED: data["model"]["value"]["public"]["asympdetected"],
            Stage.SEVERE: data["model"]["value"]["public"]["severe"],
            Stage.RECOVERED: data["model"]["value"]["public"]["recovered"],
            Stage.DECEASED: data["model"]["value"]["public"]["deceased"]
        }
    }
    print(iterative_input)
    model_params = {
        "num_agents": iterative_input[0],
        "width": iterative_input[1][0],
        "height": iterative_input[1][1],
        "repscaling": data["model"]["epidemiology"]["repscaling"],
        "kmob": data["model"]["epidemiology"]["kmob"],
        "age_mortality": age_mortality,
        "sex_mortality": sex_mortality,
        "age_distribution": age_distribution,
        "sex_distribution": sex_distribution,
        "prop_initial_infected": data["model"]["epidemiology"]["prop_initial_infected"],
        "rate_inbound": data["model"]["epidemiology"]["rate_inbound"],
        "avg_incubation_time": data["model"]["epidemiology"]["avg_incubation_time"],
        "avg_recovery_time": data["model"]["epidemiology"]["avg_recovery_time"],
        "proportion_asymptomatic": data["model"]["epidemiology"]["proportion_asymptomatic"],
        "proportion_severe": data["model"]["epidemiology"]["proportion_severe"],
        "prob_contagion": data["model"]["epidemiology"]["prob_contagion"],
        "proportion_beds_pop": data["model"]["epidemiology"]["proportion_beds_pop"],
        "proportion_isolated": data["model"]["policies"]["isolation"]["proportion_isolated"],
        "day_start_isolation": data["model"]["policies"]["isolation"]["day_start_isolation"],
        "days_isolation_lasts": data["model"]["policies"]["isolation"]["days_isolation_lasts"],
        "after_isolation": data["model"]["policies"]["isolation"]["after_isolation"],
        "prob_isolation_effective": data["model"]["policies"]["isolation"]["prob_isolation_effective"],
        "social_distance": data["model"]["policies"]["distancing"]["social_distance"],
        "day_distancing_start": data["model"]["policies"]["distancing"]["day_distancing_start"],
        "days_distancing_lasts": data["model"]["policies"]["distancing"]["days_distancing_lasts"],
        "proportion_detected": data["model"]["policies"]["testing"]["proportion_detected"],
        "day_testing_start": data["model"]["policies"]["testing"]["day_testing_start"],
        "days_testing_lasts": data["model"]["policies"]["testing"]["days_testing_lasts"],
        "day_tracing_start": data["model"]["policies"]["tracing"]["day_tracing_start"],
        "days_tracing_lasts": data["model"]["policies"]["tracing"]["days_tracing_lasts"],
        "new_agent_proportion": data["model"]["policies"]["massingress"]["new_agent_proportion"],
        "new_agent_start": data["model"]["policies"]["massingress"]["new_agent_start"],
        "new_agent_lasts": data["model"]["policies"]["massingress"]["new_agent_lasts"],
        "new_agent_age_mean": data["model"]["policies"]["massingress"]["new_agent_age_mean"],
        "new_agent_prop_infected": data["model"]["policies"]["massingress"]["new_agent_prop_infected"],
        "stage_value_matrix": value_distibution,
        "test_cost": data["model"]["value"]["test_cost"],
        "alpha_private": data["model"]["value"]["alpha_private"],
        "alpha_public": data["model"]["value"]["alpha_public"],
        "day_vaccination_begin": data["model"]["policies"]["vaccine_rollout"]["day_vaccination_begin"],
        "day_vaccination_end": data["model"]["policies"]["vaccine_rollout"]["day_vaccination_end"],
        "effective_period": data["model"]["policies"]["vaccine_rollout"]["effective_period"],
        "effectiveness": data["model"]["policies"]["vaccine_rollout"]["effectiveness"],
        "distribution_rate": data["model"]["policies"]["vaccine_rollout"]["distribution_rate"],
        "cost_per_vaccine":data["model"]["policies"]["vaccine_rollout"]["cost_per_vaccine"],
        "vaccination_percent": data["model"]["policies"]["vaccine_rollout"]["vaccination_percent"],
        "step_count": data["ensemble"]["steps"],
        "load_from_file": data["model"]["initialization"]["load_from_file"],
        "loading_file_path": data["model"]["initialization"]["loading_file_path"],
        "starting_step":data["model"]["initialization"]["starting_step"],
        "agent_storage" : data["output"]["agent_storage"],
        "model_storage": data["output"]["model_storage"],
        "agent_increment": data["output"]["agent_increment"],
        "model_increment": data["output"]["model_increment"],
        "vector_movement" : False
    }

    #Adds variant data into the model in the form of a list.
    virus_param_list = []
    for virus in virus_data["variant"]:
        virus_param_list.append(virus_data["variant"][virus])
    model_params["variant_data"] = virus_param_list
    var_params = {"dummy": range(25,50,25)}

    num_iterations = data["ensemble"]["runs"]
    num_steps = data["ensemble"]["steps"]

    batch_run = BatchRunnerMP(
        CovidModel,
        nr_processes=num_iterations,
        fixed_parameters=model_params,
        variable_parameters=var_params,
        iterations=num_iterations,
        max_steps=num_steps,
        model_reporters={
                    "Step": compute_stepno,
                    "CummulPrivValue": compute_cumul_private_value,
                    "CummulPublValue": compute_cumul_public_value,
                    "CummulTestCost": compute_cumul_testing_cost,
                    "Rt": compute_eff_reprod_number,
                    "Employed": compute_employed,
                    "Unemployed": compute_unemployed
                },
        display_progress=True)

    print("Parametrization complete:")
    print("")
    print(f"Running file {filenames_list[index]}")
    print("")
    print(f"Executing an ensemble of size {num_iterations} using {num_steps} steps with {num_iterations} machine cores...")

    #Will now return a dictionary containing [iteration:[model_data, agent_data]]
    cm_runs = batch_run.run_all()

    # Extracting data into distinct dataframes
    model_ldfs = []
    agent_ldfs = []
    i = 0
    for cm in cm_runs.values():
        cm[0]["Iteration"] = i
        cm[1]["Iteration"] = i
        model_ldfs.append(cm[0])
        agent_ldfs.append(cm[1])
        i = i + 1

    model_dfs = pd.concat(model_ldfs)
    agent_dfs = pd.concat(agent_ldfs)
    model_save_file = data["output"]["model_save_file"]
    agent_save_file = data["output"]["agent_save_file"]

    # TODO-create the nomenclature for the nature of the save file for both model and agent data. (Very important for organizing test runs for different policy evaluations)
    #Iterative input can be used to directly name the model of interest.
    model_dfs.to_csv(model_save_file + "_" + str(iterative_input) + ".csv")
    agent_dfs.to_csv(agent_save_file + "_" + str(iterative_input) + ".csv")

    print(f"Simulation {index} completed without errors.")





#Here is where we put the model verification process.
if __name__ == '__main__':
    processes = []

    space_list = [(25,25), (50,50), (75,75), (100,100), (125,125), (150,150)]
    population_list = [100,150,200,250,300]
    for index, data in enumerate(data_list):
        # Verification process:

        # 1. Initialize Differential model for a fixed parameter
        # 2. Run a parameter sweep for R0 that minimizes the lsq between the two models.
        # 3. Run trial for varying parameters for R_diff.
        # 4. Save the values of R_diff and R_abm and find some relating factor in between them.


        #2. Parameter sweep algorithm
        # For maximumm efficiency we will run trials of #2000 steps in a fixed environment.
        # We will run all 32 iterations in parallel and average the results and their variation values.
        # We evaluate the lsq for the model at that point.
        # Based on the size of the R(w) and whether it was an overestimate or under, we will reshift the prop_contagtion parameter.
        # One thing to note are all the parameters in the OG model and how they affect the overall effect on the model.
        for population in population_list:
            for space in space_list:
                variable = (population, space)
                p = multiprocessing.Process(target=runModelScenario, args=[data, index, variable])
                p.start()
                processes.append(p)
                for process in processes:
                    process.join()

