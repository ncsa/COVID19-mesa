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
import timeit
import re



def runModelScenario(data, index,virus_data):

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

    model_params = {
        "num_agents": data["model"]["epidemiology"]["num_agents"],
        "width": data["model"]["epidemiology"]["width"],
        "height": data["model"]["epidemiology"]["height"],
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
        "starting_step": data["model"]["initialization"]["starting_step"],
        "agent_storage": data["output"]["agent_storage"],
        "model_storage": data["output"]["model_storage"],
        "agent_increment":  data["output"]["agent_increment"],
        "model_increment":  data["output"]["model_increment"]
    }
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
        iterations= num_iterations,
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
        agent_reporters={},
        display_progress=True)

    print("Parametrization complete:")
    print("")
    print("")
    print(f"Executing an ensemble of size {num_iterations} using {num_steps} steps with {num_iterations} machine cores for agents...")

    cm_runs = batch_run.run_all()
    print("")
    print("Saving results to file...")

    model_ldfs = []
    agent_ldfs = []


    time_A = timeit.default_timer()
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

    #TODO-create the nomenclature for the nature of the save file for both model and agent data. (Very important for organizing test runs for different policy evaluations)
    model_dfs.to_csv(model_save_file)
    agent_dfs.to_csv(agent_save_file)
    time_B = timeit.default_timer()
    return (time_B - time_A)


    #The model_data and agent_data can now be saved into seperate locations and is determined by ->
    # if(data["model"]["initialization"]["load_from_file"]):
    #     path = data["model"]["initialization"]["loading_file_path"]
    #     print(path)
    #     iteration = path.replace(".csv", "")
    #     iteration = int(iteration[len(iteration)-1])
    #     path = path.replace(".csv", str(iteration+1)+ ".csv" )
    #     dfs.to_csv(path)
    #     print(f"Saved file to {path}")
    # else:
    #     dfs.to_csv(file_out_A)
    #
    #
    # print(f"Simulation {index} completed without errors.")


if __name__ == '__main__':
    directory_list = []
    filenames_list = []
    begin = int(sys.argv[1])
    end = int(sys.argv[2])
    print(begin, end)

    print(sys.argv[4:])

    virus_data_file = open(str(sys.argv[3]))
    for argument in sys.argv[4:]:
        directory_list.append(str(argument))

    for directory in directory_list:
        file_list = glob.glob(f"{directory}/*.json")
        for file in file_list:
            filenames_list.append(file)
    # Read JSON file
    data_list = []
    name = ""
    for file_params in filenames_list:
        with open(file_params) as f:
            data = json.load(f)
            data_list.append(data)

    indexes = [range(len(data_list))]

    virus_data = json.load(virus_data_file)

    total_iterations = 0
    parameters = []
    for index, data in enumerate(data_list):
        parameter = []
        total_iterations += data["ensemble"]["runs"]
        parameter.append(data)
        parameter.append(index)
        parameter.append(virus_data)
        parameters.append(parameter)

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    processes = []
    for parameter in parameters:
        process = multiprocessing.Process(target = runModelScenario, args = parameter)
        process.start()
        processes.append(process)

    for _ in range(len(processes)):
        process.join()










