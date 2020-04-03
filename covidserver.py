# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

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

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5}

    if agent.stage == Stage.SUSCEPTIBLE:
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
    elif agent.stage == Stage.INCUBATING:
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    elif agent.stage == Stage.ASYMPTOMATIC:
        portrayal["Color"] = "brown"
        portrayal["Layer"] = 0
    elif agent.stage == Stage.SYMPDETECTED:
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 0
    elif agent.stage == Stage.ASYMPDETECTED:
        portrayal["Color"] = "cyan"
        portrayal["Layer"] = 0
    elif agent.stage == Stage.SEVERE:
        portrayal["Color"] = "magenta"
        portrayal["Layer"] = 0
    elif agent.stage == Stage.RECOVERED:
        portrayal["Color"] = "green"
        portrayal["Layer"] = 0
    elif agent.stage == Stage.DECEASED:
        portrayal["Color"] = "black"
        portrayal["Layer"] = 0
    elif agent.locked:
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 0
    else:
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 0

    return portrayal

grid = CanvasGrid(agent_portrayal, 50, 50, 400, 400)

chart = ChartModule([{"Label": "Susceptible",
                      "Color": "Blue"},
                      {"Label": "Incubating",
                      "Color": "Red"},
                      {"Label": "Asymptomatic",
                      "Color": "Brown"},
                      {"Label": "SymptQuarantined",
                      "Color": "Yellow"},
                      {"Label": "AsymptQuarantined",
                      "Color": "Cyan"},
                      {"Label": "Recovered",
                      "Color": "Green"},
                      {"Label": "Severe",
                      "Color": "Magenta"},
                      {"Label": "Deceased",
                      "Color": "Black"},
                      {"Label": "Locked",
                      "Color": "Gray"},
                      ],
                    data_collector_name='datacollector')

model_params = {
    "N":255,
    "width":50,
    "height":50,
    "distancing": False,
    "amort": cr_age_mortality,
    "smort": cr_sex_mortality,
    "adist": cr_age_distribution,
    "sdist": cr_sex_distribution,
    "avinc": UserSettableParameter("slider", "Average incubation time", 5, 2, 24, 1),
    "avrec": UserSettableParameter("slider", "Average recovery time", 15, 15, 30, 1),
    "pasympt": UserSettableParameter("slider", "Proportion of asymptomatics", 0.2, 0.0, 1.0, 0.05),
    "pcont": UserSettableParameter("slider", "Probability of contagion", 0.04, 0.0, 0.15, 0.01),
    "pdet": UserSettableParameter("slider", "Probability of detection", 0.2, 0.0, 1.0, 0.05),
    "plock": UserSettableParameter("slider", "Proportion in shelter-at-home", 0.0, 0.0, 1.0, 0.05),
    "peffl": UserSettableParameter("slider", "Shelter-at-home effectiveness", 0.0, 0.0, 1.0, 0.05),
    "psev": UserSettableParameter("slider", "Proportion of severe cases", 0.13, 0.0, 0.20, 0.01),
    "ddet": UserSettableParameter("slider", "Days before massive testing", 10, 1, 60, 1),
    "dimp": UserSettableParameter("slider", "Massive testing duration", 8, 1, 60, 1)
}

server = ModularServer(CovidModel,
                       [grid, chart],
                       "COVID-19 agent spread model - San Jose, Costa Rica",
                       model_params
                       )

server.port = 8521 # The default
server.launch()