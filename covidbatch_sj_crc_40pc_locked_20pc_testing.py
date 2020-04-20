# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from batchrunner_local import BatchRunnerMP
from covidmodel import CovidModel
from covidmodel import CovidModel
from covidmodel import Stage
from covidmodel import AgeGroup
from covidmodel import SexGroup
from covidmodel import LockGroup
from covidmodel import ValueGroup
import pandas as pd
from multiprocessing import freeze_support
from covidmodel import *

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
    AgeGroup.C80toXX: 0.023,
    AgeGroup.C70to79: 0.03,
    AgeGroup.C60to69: 0.078,
    AgeGroup.C50to59: 0.109,
    AgeGroup.C40to49: 0.128,
    AgeGroup.C30to39: 0.169,
    AgeGroup.C20to29: 0.169,
    AgeGroup.C10to19: 0.148,
    AgeGroup.C00to09: 0.146
}

# Observed distribution of mortality rage per sex
cr_sex_distribution = {
    SexGroup.MALE: 0.496,
    SexGroup.FEMALE: 0.504
}

# Value distribution per stage per interaction (micro vs macroeconomics)
cr_value_distibution = {
    ValueGroup.PERSONAL: {
        Stage.SUSCEPTIBLE: 1.0,
        Stage.INCUBATING: 1.0,
        Stage.SYMPDETECTED: -0.2,
        Stage.ASYMPTOMATIC: 1.0,
        Stage.ASYMPDETECTED: -0.2,
        Stage.SEVERE: -5.0,
        Stage.RECOVERED: 0.8,
        Stage.DECEASED: 0
    },
    ValueGroup.PUBLIC: {
        Stage.SUSCEPTIBLE: 10.0,
        Stage.INCUBATING: 10.0,
        Stage.SYMPDETECTED: -20.0,
        Stage.ASYMPTOMATIC: 10.0,
        Stage.ASYMPDETECTED: -25,
        Stage.SEVERE: -250.0,
        Stage.RECOVERED: 5,
        Stage.DECEASED: -1
    }
}

model_params = {
    "N": 250,
    "width":50,
    "height":50,
    "dist": False,
    "amort": cr_age_mortality,
    "smort": cr_sex_mortality,
    "adist": cr_age_distribution,
    "sdist": cr_sex_distribution,
    "avinc": 9,
    "avrec": 20,
    "pasympt": 0.2,
    "pcont": 0.04,
    "pdet": 0.2,
    "plock": 0.4,
    "peffl": 1.0,
    "psev": 0.10,
    "ddet": 20,
    "dimp": 7,
    "stvald": cr_value_distibution,
    "tcost": 200,
    "aper": 1.0,
    "apub": 1.0
}

var_params = {"dummy": range(25,50,25)}

num_iterations = 12
num_steps = 14000

if __name__ == "__main__":
    freeze_support()

    batch_run = BatchRunnerMP(
        CovidModel,
        nr_processes=3,
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
                    "CummulPrivValue": compute_commul_private_value,
                    "CummulPublValue": compute_commul_public_value,
                    "CummulTestCost": compute_commul_testing_cost,
                    "Rt": compute_eff_reprod_number
                },)


    cm_runs = batch_run.run_all()

    ldfs = []
    i = 0

    for cm in cm_runs.values():
        cm["Iteration"] = i
        ldfs.append(cm)
        i = i + 1

    dfs = pd.concat(ldfs)
    dfs.to_csv("sj_crc_40l_20t_test.csv")
    