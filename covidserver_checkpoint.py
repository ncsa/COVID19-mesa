# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from CanvasGridVisualization_local import CanvasGrid
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
import sys
import json
from covidmodelcheckpoint import CovidModel
from covidmodelcheckpoint import Stage
from covidmodelcheckpoint import AgeGroup
from covidmodelcheckpoint import SexGroup
from covidmodelcheckpoint import ValueGroup
import numpy as np

# Specific model data

virus_data_file = open(sys.argv[1])
virus_data = json.load(virus_data_file)
virus_param_list = []
for virus in virus_data["variant"]:
    virus_param_list.append(virus_data["variant"][virus])
print(virus_param_list)
max_hex = 2**24



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
    ValueGroup.PRIVATE: {
        Stage.SUSCEPTIBLE: 1.0,
        Stage.EXPOSED: 1.0,
        Stage.SYMPDETECTED: -0.2,
        Stage.ASYMPTOMATIC: 1.0,
        Stage.ASYMPDETECTED: -0.2,
        Stage.SEVERE: -5.0,
        Stage.RECOVERED: 0.8,
        Stage.DECEASED: 0
    },
    ValueGroup.PUBLIC: {
        Stage.SUSCEPTIBLE: 10.0,
        Stage.EXPOSED: 10.0,
        Stage.SYMPDETECTED: -5.0,
        Stage.ASYMPTOMATIC: 10.0,
        Stage.ASYMPDETECTED: -1.0,
        Stage.SEVERE: -30.0,
        Stage.RECOVERED: 5,
        Stage.DECEASED: -5
    }
}

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 3,
                 "r": 0.5}
    if agent.vaccinated:
        portrayal["Color"] = "lime"
        portrayal["Layer"] = 3
    elif agent.stage == Stage.SUSCEPTIBLE:
        portrayal["Color"] = "blue"
        portrayal["Layer"] =  3
    elif agent.stage == Stage.EXPOSED:
        portrayal["Color"] = "red"
        portrayal["Layer"] =  3
    elif agent.stage == Stage.ASYMPTOMATIC:
        portrayal["Color"] = "brown"
        portrayal["Layer"] = 3
    elif agent.stage == Stage.SYMPDETECTED:
        portrayal["Color"] = "yellow"
        portrayal["Layer"] = 3
    elif agent.stage == Stage.ASYMPDETECTED:
        portrayal["Color"] = "cyan"
        portrayal["Layer"] = 3
    elif agent.stage == Stage.SEVERE:
        portrayal["Color"] = "magenta"
        portrayal["Layer"] = 3
    elif agent.stage == Stage.RECOVERED:
        portrayal["Color"] = "green"
        portrayal["Layer"] = 3
    elif agent.stage == Stage.DECEASED:
        portrayal["Color"] = "black"
        portrayal["Layer"] = 3
    elif agent.locked:
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 3
    else:
        portrayal["Color"] = "gray"
        portrayal["Layer"] = 3

    return portrayal

def space_portrayal(options):
    space = {"Shape": "rect",
                 "Filled": "true",
                 "Layer": 1,
                 "w": 0.98,
                 "h":0.98}
    direction = {"Shape": "arrowHead",
                 "Filled": "true",
                 "Layer": 2,
                 "scale": 0.0,
                 "Color": "black"}
    vector = options[2]
    if len(options[1]) > 2:
        stationary_chance  = 0
        for index, item in enumerate(options[0]):
            if item == (0,0):
                stationary_chance = options[1][index]
        hexidec = f"{hex(int(max_hex * stationary_chance))}"
        hexi = hexidec.replace("0x", "")
        if (len(hexi) < 6):
            hexi = "0" + hexi
        HTMLcol = "#" + hexi

        space["Color"] = HTMLcol.upper()
        if (len(HTMLcol.upper())<7):
            print(stationary_chance, hexidec, HTMLcol, HTMLcol.upper(), options)
        space["Layer"] = 0
    else:
        space["Color"] = "white"
        space["Layer"] = 0

    # unit = (0,0)
    # for index, item in enumerate(options[0]):
    #     if not(item[0] == 0 and item[1] == 0):
    #         if(item[0] == 0 and item[1] != 0):
    #             unit = item
    #         elif(item[1] == 0 and item[0] != 0):
    #             unit = item
    #
    # direction["heading_x"] = unit[0]
    # direction["heading_y"] = unit[1]
    return space, None

grid = CanvasGrid(agent_portrayal,space_portrayal , 50, 50, 800, 800)

chart = ChartModule([{"Label": "N",
                      "Color": "Darkblue"},
                      {"Label": "SUSCEPTIBLE",
                      "Color": "Blue"},
                      {"Label": "EXPOSED",
                      "Color": "Red"},
                      {"Label": "ASYMPTOMATIC",
                      "Color": "Brown"},
                      {"Label": "SYMPDETECTED",
                      "Color": "Yellow"},
                      {"Label": "ASYMPDETECTED",
                      "Color": "Cyan"},
                      {"Label": "RECOVERED",
                      "Color": "Green"},
                      {"Label": "SEVERE",
                      "Color": "Magenta"},
                      {"Label": "DECEASED",
                      "Color": "Black"},
                      {"Label": "Isolated",
                      "Color": "Gray"},
                     {"Label": "Vaccinated",
                      "Color": "Gold"},
                     {"Label": "Vaccine_Willing",
                      "Color": "Lime"}
                     ],
                    data_collector_name='datacollector')


Achart = ChartModule([{"Label": "Alpha_Variant_Total_Infected",
                      "Color": "Blue"},
                      {"Label": "Alpha_VariantEXPOSED",
                      "Color": "Red"},
                      {"Label": "Alpha_VariantASYMPTOMATIC",
                      "Color": "Brown"},
                      {"Label": "Alpha_VariantSYMPDETECTED",
                      "Color": "Yellow"},
                      {"Label": "Alpha_VariantASYMPDETECTED",
                      "Color": "Cyan"},
                      {"Label": "Alpha_VariantRECOVERED",
                      "Color": "Green"},
                      {"Label": "Alpha_VariantSEVERE",
                      "Color": "Magenta"},
                      {"Label": "Alpha_VariantDECEASED",
                      "Color": "Black"}
                     ],
                    data_collector_name='datacollector')


Bchart = ChartModule([{"Label": "Beta_Variant_Total_Infected",
                      "Color": "Blue"},
                      {"Label": "Beta_VariantEXPOSED",
                      "Color": "Red"},
                      {"Label": "Beta_VariantASYMPTOMATIC",
                      "Color": "Brown"},
                      {"Label": "Beta_VariantSYMPDETECTED",
                      "Color": "Yellow"},
                      {"Label": "Beta_VariantASYMPDETECTED",
                      "Color": "Cyan"},
                      {"Label": "Beta_VariantRECOVERED",
                      "Color": "Green"},
                      {"Label": "Beta_VariantSEVERE",
                      "Color": "Magenta"},
                      {"Label": "Beta_VariantDECEASED",
                      "Color": "Black"}
                     ],
                    data_collector_name='datacollector')

Dchart = ChartModule([{"Label": "Delta_Variant_Total_Infected",
                      "Color": "Blue"},
                      {"Label": "Delta_VariantEXPOSED",
                      "Color": "Red"},
                      {"Label": "Delta_VariantASYMPTOMATIC",
                      "Color": "Brown"},
                      {"Label": "Delta_VariantSYMPDETECTED",
                      "Color": "Yellow"},
                      {"Label": "Delta_VariantASYMPDETECTED",
                      "Color": "Cyan"},
                      {"Label": "Delta_VariantRECOVERED",
                      "Color": "Green"},
                      {"Label": "Delta_VariantSEVERE",
                      "Color": "Magenta"},
                      {"Label": "Delta_VariantDECEASED",
                      "Color": "Black"}
                     ],
                    data_collector_name='datacollector')



chart_personal_value = ChartModule([{"Label": "CumulPrivValue",
                      "Color": "Black"}
                      ],
                    data_collector_name='datacollector'
)

chart_public_value = ChartModule([
                      {"Label": "CumulPublValue",
                      "Color": "Red"},
                      {"Label": "CumulTestCost",
                      "Color": "Green"}
                      ],
                    data_collector_name='datacollector'
)


chart_cumulative_effectiveness = ChartModule([
                      {"Label": "Cumulative_Effectiveness C00to09",
                      "Color": "Red"},
                      {"Label": "Cumulative_Effectiveness C10to19",
                      "Color": "Green"},
                      {"Label": "Cumulative_Effectiveness C20to29",
                      "Color": "Blue"},
                      {"Label": "Cumulative_Effectiveness C30to39",
                      "Color": "Orange"},
                      {"Label": "Cumulative_Effectiveness C40to49",
                      "Color": "Gold"},
                      {"Label": "Cumulative_Effectiveness C50to59",
                      "Color": "Magenta"},
                      {"Label": "Cumulative_Effectiveness C60to69",
                      "Color": "Black"},
                      {"Label": "Cumulative_Effectiveness C70to79",
                      "Color": "Gray"},
                      {"Label": "Cumulative_Effectiveness C80toXX",
                      "Color": "Lime"}
                      ],
                    data_collector_name='datacollector'
)

chart_cumulative_effectiveness = ChartModule([
                      {"Label": "Cumulative_Effectiveness C00to09",
                      "Color": "Red"},
                      {"Label": "Cumulative_Effectiveness C10to19",
                      "Color": "Green"},
                      {"Label": "Cumulative_Effectiveness C20to29",
                      "Color": "Blue"},
                      {"Label": "Cumulative_Effectiveness C30to39",
                      "Color": "Orange"},
                      {"Label": "Cumulative_Effectiveness C40to49",
                      "Color": "Gold"},
                      {"Label": "Cumulative_Effectiveness C50to59",
                      "Color": "Magenta"},
                      {"Label": "Cumulative_Effectiveness C60to69",
                      "Color": "Black"},
                      {"Label": "Cumulative_Effectiveness C70to79",
                      "Color": "Gray"},
                      {"Label": "Cumulative_Effectiveness C80toXX",
                      "Color": "Lime"}
                      ],
                    data_collector_name='datacollector'
)

vaccinated_age_group = ChartModule([
                      {"Label": "Vaccinated C00to09",
                      "Color": "Red"},
                      {"Label": "Vaccinated C10to19",
                      "Color": "Green"},
                      {"Label": "Vaccinated C20to29",
                      "Color": "Blue"},
                      {"Label": "Vaccinated C30to39",
                      "Color": "Orange"},
                      {"Label": "Vaccinated C40to49",
                      "Color": "Gold"},
                      {"Label": "Vaccinated C50to59",
                      "Color": "Magenta"},
                      {"Label": "Vaccinated C60to69",
                      "Color": "Black"},
                      {"Label": "Vaccinated C70to79",
                      "Color": "Gray"},
                      {"Label": "Vaccinated C80toXX",
                      "Color": "Lime"}
                      ],
                    data_collector_name='datacollector'
)

chart_epidemiology = ChartModule([
                      {"Label": "Rt",
                      "Color": "Blue"
                      },
                      ],
                    data_collector_name='datacollector'
)

chart_number = ChartModule([
                      {"Label": "N",
                      "Color": "Blue"
                      },
                      ],
                    data_collector_name='datacollector'
)

chart_employment = ChartModule([
                      {"Label": "Employed",
                      "Color": "Blue"},
                      {"Label": "Unemployed",
                      "Color": "Red"}
                      ],
                    data_collector_name='datacollector'
)

chart_tested = ChartModule([
                      {"Label": "Tested",
                      "Color": "Orange"},
                      {"Label": "Traced",
                      "Color": "Magenta"}
                      ],
                    data_collector_name='datacollector'
)
chart_vaccines = ChartModule([
                      {"Label": "Vaccines",
                      "Color": "Green"},
                    ],
                    data_collector_name='datacollector'
)

model_params = {
    "num_agents": 260,
    "width": 50,
    "height": 50,
    "repscaling": 1,
    "kmob": 1,
    "after_isolation": 0.1,
    "age_mortality": cr_age_mortality,
    "sex_mortality": cr_sex_mortality,
    "age_distribution": cr_age_distribution,
    "sex_distribution": cr_sex_distribution,
    "prop_initial_infected": UserSettableParameter("slider", "Proportion of initially infected", 0.04, 0.0, 1, 0.001),
    "rate_inbound": UserSettableParameter("slider", "Inbound infections", 0.001, 0.0, 0.1, 0.001), 
    "avg_incubation_time": UserSettableParameter("slider", "Average incubation time", 1, 2, 24, 1),
    "avg_recovery_time": UserSettableParameter("slider", "Average recovery time", 15, 0 , 30, 1),
    "proportion_asymptomatic": UserSettableParameter("slider", "Proportion of asymptomatics", 0.2, 0.0, 1.0, 0.05),
    "proportion_severe": UserSettableParameter("slider", "Proportion of severe cases", 0.13, 0.0, 0.20, 0.01),
    "prob_contagion": UserSettableParameter("slider", "Probability of contagion", 0.0130, 0.0, 0.6, 0.005),
    "proportion_beds_pop": UserSettableParameter("slider", "Proportion of hospital beds per population size", 0.01, 0.0, 0.1, 0.001),
    "proportion_isolated": UserSettableParameter("slider", "Proportion isolated", 0.0, 0.0, 1.0, 0.05),
    "day_start_isolation": UserSettableParameter("slider", "Isolation policy start (days) ", 365, 0, 365, 2),
    "days_isolation_lasts": UserSettableParameter("slider", "Duration of isolation policy ", 365, 0, 365, 2),
    "prob_isolation_effective": UserSettableParameter("slider", "Isolation effectiveness", 1.0, 0.0, 1.0, 0.05),
    "social_distance": UserSettableParameter("slider", "Social distance (meters)", 1.8, 0.0, 2.5, 0.1),
    "day_distancing_start": UserSettableParameter("slider", "Social distancing policy start (days) ", 365, 0, 365, 2),
    "days_distancing_lasts": UserSettableParameter("slider", "Duration of social distancing policy ", 365, 0, 365, 5),
    "proportion_detected": UserSettableParameter("slider", "Proportion of detected cases", 0.1, 0.0, 1.0, 0.05),
    "day_testing_start": UserSettableParameter("slider", "Generalized testing policy start (days) ", 365, 0, 365, 2),
    "days_testing_lasts": UserSettableParameter("slider", "Duration of generalized testing policy ", 365, 0, 365, 2),
    "day_tracing_start": UserSettableParameter("slider", "Generalized testing policy start (days) ", 365, 0, 365, 2),
    "days_tracing_lasts": UserSettableParameter("slider", "Duration of generalized testing policy ", 365, 0, 365, 2),
    "new_agent_proportion": UserSettableParameter("slider", "Proportion of current pop. for massive entry", 0.1, 0.0, 1.0, 0.05),
    "new_agent_start": UserSettableParameter("slider", "Massive entry start (days) ", 365, 0, 365, 2),
    "new_agent_lasts": UserSettableParameter("slider", "Duration of massive entry ", 365, 0, 365, 2),
    "new_agent_age_mean": UserSettableParameter("slider", "Average age group for massive entry ", 2, 0, 8, 1),
    "new_agent_prop_infected": UserSettableParameter("slider", "Inbound infections", 0.001, 0.0, 0.1, 0.001),
    "stage_value_matrix": cr_value_distibution,
    "test_cost": 200,
    "alpha_private": UserSettableParameter("slider", "Personal value amplifier", 1.0, 0.0, 2.0, 0.1),
    "alpha_public": UserSettableParameter("slider", "Public value amplifier", 1.0, 0.0, 2.0, 0.1),
    "day_vaccination_begin": UserSettableParameter("slider", "day_vaccination_begin", 5, 0, 100, 1),
    "day_vaccination_end": UserSettableParameter("slider", "day_vaccination_end", 40, 300, 2000, 1),
    "effective_period": UserSettableParameter("slider", "effective_period", 10, 10, 365, 5),
    "effectiveness": UserSettableParameter("slider", "effectiveness", 0.9, 0.0, 1.0, 0.01),
    "distribution_rate": UserSettableParameter("slider", "distribution rate", 20, 0, 100, 1),
    "cost_per_vaccine": UserSettableParameter("slider", "cost_per_vaccine", 200, 10, 1000, 10),
    "vaccination_percent": UserSettableParameter("slider", "vaccination_percent", 0.5, 0, 1, 0.01),
    "variant_data": virus_param_list,
    "step_count": UserSettableParameter("slider", "vaccination_percent", 192, 0, 9600, 96),
    "load_from_file": False,
    "loading_file_path": None,
    "starting_step": 0,
    "agent_storage": 0,
    "model_storage": -1,
    "agent_increment":0,
    "model_increment":1,
    "iteration":1
}
server = ModularServer(CovidModel,
                       [grid,chart,chart_epidemiology,chart_cumulative_effectiveness,vaccinated_age_group,Achart,Bchart,Dchart],
                       "COVID-19 epidemiological and economic model",
                       model_params
                       )

server.port = 8521 # The default
server.launch()