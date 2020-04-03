# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from mesa.batchrunner import BatchRunner
from covidmodel import CovidModel
import pandas as pd


from covidmodel import CovidModel
from covidmodel import Stage
from covidmodel import AgeGroup
from covidmodel import SexGroup
from covidmodel import LockGroup
from covidmodel import compute_susceptible
from covidmodel import compute_incubating
from covidmodel import compute_asymptomatic
from covidmodel import compute_symptdetected
from covidmodel import compute_asymptdetected
from covidmodel import compute_severe
from covidmodel import compute_deceased
from covidmodel import compute_recovered
from covidmodel import compute_locked

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

model_params = {
    "N":3904,
    "width":200,
    "height":200,
    "distancing": False,
    "amort": cr_age_mortality,
    "smort": cr_sex_mortality,
    "adist": cr_age_distribution,
    "sdist": cr_sex_distribution,
    "avinc": 5,
    "avrec": 15,
    "pasympt": 0.2,
    "pcont": 0.04,
    "pdet": 0.0,
    "plock": 0.0,
    "peffl": 0.0,
    "psev": 0.13,
    "ddet": 10,
    "dimp": 8
}

batch_run = BatchRunner(
    CovidModel,
    {},
    model_params,
    iterations=10,
    max_steps=300,
    model_reporters = {
        "Susceptible": compute_susceptible,
        "Incubating": compute_incubating,
        "Asymptomatic": compute_asymptomatic,
        "SymptQuarantined": compute_symptdetected,
        "AsymptQuarantined": compute_asymptdetected,
        "Severe": compute_severe,
        "Recovered": compute_recovered,
        "Deceased": compute_deceased,
        "Isolated": compute_locked
    }
)

batch_run.run_all()
run_data = batch_run.get_model_vars_dataframe()
run_data.to_csv("cr_no_measures_ensemb.csv")
