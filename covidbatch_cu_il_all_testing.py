# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from mesa.batchrunner import BatchRunner
from covidmodel import CovidModel
from covidmodel import CovidModel
from covidmodel import Stage
from covidmodel import AgeGroup
from covidmodel import SexGroup
from covidmodel import LockGroup
import pandas as pd


# Specific model data

# Observed distribution of mortality rate per age
cr_age_mortality = {
    AgeGroup.C80toXX: 0.148,
    AgeGroup.C70to79: 0.08,
    AgeGroup.C60to69: 0.036,
    AgeGroup.C50to59: 0.013,
    AgeGroup.C40to49: 0.004,
    AgeGroup.C30to39: 0.002,
    AgeGroup.C20to29: 0.002,
    AgeGroup.C10to19: 0.002,
    AgeGroup.C00to09: 0.0
}

# Observed distribution of mortality rage per sex
cr_sex_mortality = {
    SexGroup.MALE: 0.62,
    SexGroup.FEMALE: 0.38
}

cr_age_distribution = {
    AgeGroup.C80toXX: 0.03,
    AgeGroup.C70to79: 0.04,
    AgeGroup.C60to69: 0.075,
    AgeGroup.C50to59: 0.075,
    AgeGroup.C40to49: 0.07,
    AgeGroup.C30to39: 0.125,
    AgeGroup.C20to29: 0.3,
    AgeGroup.C10to19: 0.2,
    AgeGroup.C00to09: 0.085
}

# Observed distribution of mortality rage per sex
cr_sex_distribution = {
    SexGroup.MALE: 0.505,
    SexGroup.FEMALE: 0.495
}

model_params = {
    "N":250,
    "width":68,
    "height":68,
    "distancing": False,
    "amort": cr_age_mortality,
    "smort": cr_sex_mortality,
    "adist": cr_age_distribution,
    "sdist": cr_sex_distribution,
    "avinc": 7,
    "avrec": 20,
    "pasympt": 0.25,
    "pcont": 0.04,
    "pdet": 1.0,
    "plock": 0.5,
    "peffl": 1.0,
    "psev": 0.10,
    "ddet": 40,
    "dimp": 7
}

num_iterations = 12
num_steps = 12000

#batch_run = BatchRunner(
#    CovidModel,
#    fixed_parameters=model_params,
#    iterations=num_iterations,
#    max_steps=num_steps,
#    model_reporters = {
#        "Data collector": lambda m: m.datacollector
#    }
#)

#batch_run.run_all()

# Unify all into a single dataframe for storage
#run_data = batch_run.get_model_vars_dataframe()
ldfs = []

for i in range(num_iterations):
    print(f"Iteration {i}")
    cm = CovidModel(model_params["N"],
                model_params["width"],
                model_params["height"],
                model_params["distancing"],
                model_params["pasympt"],
                model_params["amort"],
                model_params["smort"],
                model_params["avinc"],
                model_params["avrec"],
                model_params["psev"],
                model_params["adist"],
                model_params["sdist"],
                model_params["plock"],
                model_params["peffl"],
                model_params["pcont"],
                model_params["pdet"],
                model_params["ddet"],
                model_params["dimp"])
    
    for j in range(num_steps):
        cm.step()

    dft = cm.datacollector.get_model_vars_dataframe()
    dft["Iteration"] = i
    ldfs.append(dft)

dfs = pd.concat(ldfs)
dfs.to_csv("cu_il_all_testing.csv")
