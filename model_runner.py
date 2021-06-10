# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from batchrunner_local import BatchRunnerMP
from multiprocessing import freeze_support
from covidmodel import CovidModel
from covidmodel import CovidModel
from covidmodel import Stage
from covidmodel import AgeGroup
from covidmodel import SexGroup
from covidmodel import IOMatrixGroup
from covidmodel import *
import pandas as pd
import json
import sys

num_procs = int(sys.argv[1])
file_params = sys.argv[2]

# Read JSON file
with open(file_params) as f:
  data = json.load(f)

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
io_matrix = {
    IOMatrixGroup.PRIVATE: {
        Stage.SUSCEPTIBLE: data["model"]["economics"]["private"]["susceptible"],
        Stage.EXPOSED: data["model"]["economics"]["private"]["exposed"],
        Stage.SYMPDETECTED: data["model"]["economics"]["private"]["sympdetected"],
        Stage.ASYMPTOMATIC: data["model"]["economics"]["private"]["asymptomatic"],
        Stage.ASYMPDETECTED: data["model"]["economics"]["private"]["asympdetected"],
        Stage.SEVERE: data["model"]["economics"]["private"]["severe"],
        Stage.RECOVERED: data["model"]["economics"]["private"]["recovered"],
        Stage.DECEASED: data["model"]["economics"]["private"]["deceased"]
    },
    IOMatrixGroup.PUBLIC: {
        Stage.SUSCEPTIBLE: data["model"]["economics"]["public"]["susceptible"],
        Stage.EXPOSED: data["model"]["economics"]["public"]["exposed"],
        Stage.SYMPDETECTED: data["model"]["economics"]["public"]["sympdetected"],
        Stage.ASYMPTOMATIC: data["model"]["economics"]["public"]["asymptomatic"],
        Stage.ASYMPDETECTED: data["model"]["economics"]["public"]["asympdetected"],
        Stage.SEVERE: data["model"]["economics"]["public"]["severe"],
        Stage.RECOVERED: data["model"]["economics"]["public"]["recovered"],
        Stage.DECEASED: data["model"]["economics"]["public"]["deceased"]
    }
}

io_economics = {
    IOEconomics.ALPHAPRIVATE: data["model"]["economics"]["alpha_private"],
    IOEconomics.ALPHAPUBLIC: data["model"]["economics"]["alpha_public"],
    IOEconomics.TESTCOST: data["model"]["economics"]["test_cost"]
}

model_params = {
    #"prop_initial_infected": data["model"]["epidemiology"]["prop_initial_infected"],
    #"avg_recovery_time": data["model"]["epidemiology"]["avg_recovery_time"],
    #"proportion_asymptomatic": data["model"]["epidemiology"]["proportion_asymptomatic"],
    #"proportion_severe": data["model"]["epidemiology"]["proportion_asymptomatic"],
    #"proportion_beds_pop": data["model"]["epidemiology"]["proportion_beds_pop"],
    "age_mortality": age_mortality,
    "sex_mortality": sex_mortality,
    "age_distribution": age_distribution,
    "sex_distribution": sex_distribution,
    "epidemiology": data["model"]["epidemiology"],
    "policies": data["model"]["policies"],
    "io_matrix": io_matrix,
    "io_economics": io_economics
}

var_params = {"dummy": range(25,50,25)}

num_iterations = data["ensemble"]["runs"]
num_steps = data["ensemble"]["steps"]

if __name__ == "__main__":
    freeze_support()

    batch_run = BatchRunnerMP(
        CovidModel,
        nr_processes=num_procs,
        fixed_parameters=model_params,
        variable_parameters=var_params,
        iterations=num_iterations,
        max_steps=num_steps,
        model_reporters={
                    "Step": compute_stepno,
                    "Susceptible": compute_susceptible,
                    "Incubating": compute_incubating,
                    "Asymptomatic": compute_asymptomatic,
                    "SymptQuarantined": compute_symptdetected,
                    "AsymptQuarantined": compute_asymptdetected,
                    "Severe": compute_severe,
                    "Recovered": compute_recovered,
                    "Deceased": compute_deceased,
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
    print(json.dumps(data, indent=3))
    print("")
    print(f"Executing an ensemble of size {num_iterations} using {num_steps} steps with {num_procs} machine cores...")
    cm_runs = batch_run.run_all()

    print("")
    print("Saving results to file...")

    ldfs = []
    i = 0

    for cm in cm_runs.values():
        cm["Iteration"] = i
        ldfs.append(cm)
        i = i + 1

    file_out = data["output"]["prefix"]

    dfs = pd.concat(ldfs)
    dfs.to_csv(file_out + ".csv")

    print("Simulation completed without errors.")
