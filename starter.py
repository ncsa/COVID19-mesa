# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from covidmodel import CovidModel
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd


from covidmodel import CovidModel
from covidmodel import Stage
from covidmodel import AgeGroup
from covidmodel import SexGroup
from covidmodel import LockGroup

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
    "N":255,
    "width":50,
    "height":50,
    "distancing": False,
    "amort": cr_age_mortality,
    "smort": cr_sex_mortality,
    "adist": cr_age_distribution,
    "sdist": cr_sex_distribution,
    "avinc": 5,
    "avrec": 15,
    "pasympt": 0.2,
    "pcont": 0.03,
    "pdet": 0.0,
    "plock": 0.0,
    "peffl": 0.0,
    "psev": 0.03,
    "ddet": 10,
    "dimp": 8
}

cm = CovidModel(model_params["N"],
                model_params["width"],
                model_params["height"],
                False,
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

# Simulate for 90 days
for i in range(90 * cm.dwell_15_day):
    cm.step()

trends = cm.datacollector.get_model_vars_dataframe()
trends.to_csv('cr_no_measures.csv')
