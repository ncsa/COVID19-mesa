
def hello_covid(data):
    from covidmodel import CovidModel
    from covidmodel import AgeGroup, SexGroup, ValueGroup, Stage

    var_params = {"dummy": range(25, 50, 25)}

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
        "proportion_asymptomatic": data["model"]["epidemiology"][
            "proportion_asymptomatic"],
        "proportion_severe": data["model"]["epidemiology"]["proportion_asymptomatic"],
        "prob_contagion": data["model"]["epidemiology"]["proportion_asymptomatic"],
        "proportion_beds_pop": data["model"]["epidemiology"]["proportion_beds_pop"],
        "proportion_isolated": data["model"]["policies"]["isolation"][
            "proportion_isolated"],
        "day_start_isolation": data["model"]["policies"]["isolation"][
            "day_start_isolation"],
        "days_isolation_lasts": data["model"]["policies"]["isolation"][
            "days_isolation_lasts"],
        "after_isolation": data["model"]["policies"]["isolation"]["after_isolation"],
        "prob_isolation_effective": data["model"]["policies"]["isolation"][
            "prob_isolation_effective"],
        "social_distance": data["model"]["policies"]["distancing"]["social_distance"],
        "day_distancing_start": data["model"]["policies"]["distancing"][
            "day_distancing_start"],
        "days_distancing_lasts": data["model"]["policies"]["distancing"][
            "days_distancing_lasts"],
        "proportion_detected": data["model"]["policies"]["testing"][
            "proportion_detected"],
        "day_testing_start": data["model"]["policies"]["testing"]["day_testing_start"],
        "days_testing_lasts": data["model"]["policies"]["testing"]["days_testing_lasts"],
        "day_tracing_start": data["model"]["policies"]["tracing"]["day_tracing_start"],
        "days_tracing_lasts": data["model"]["policies"]["tracing"]["days_tracing_lasts"],
        "new_agent_proportion": data["model"]["policies"]["massingress"][
            "new_agent_proportion"],
        "new_agent_start": data["model"]["policies"]["massingress"]["new_agent_start"],
        "new_agent_lasts": data["model"]["policies"]["massingress"]["new_agent_lasts"],
        "new_agent_age_mean": data["model"]["policies"]["massingress"][
            "new_agent_age_mean"],
        "new_agent_prop_infected": data["model"]["policies"]["massingress"][
            "new_agent_prop_infected"],
        "stage_value_matrix": value_distibution,
        "test_cost": data["model"]["value"]["test_cost"],
        "alpha_private": data["model"]["value"]["alpha_private"],
        "alpha_public": data["model"]["value"]["alpha_public"]
    }

    num_iterations = data["ensemble"]["runs"]
    num_steps = data["ensemble"]["steps"]

    model = CovidModel(**model_params)
    for i in range(num_steps):
        model.step()

    return model.datacollector.get_model_vars_dataframe()

data = {
    "location": "Champaign-Urbana",
    "description": "Callibration run from 0.1% to 1.0% from April 21 to July 8th",
    "prepared-by": "Eric Jakobsson and Santiago Nunez-Corrales",
    "date": "2020.07.15",
    "model": {
        "distributions": {
            "age": {
                "80+": 0.03,
                "70-79": 0.04,
                "60-69": 0.075,
                "50-59": 0.075,
                "40-49": 0.07,
                "30-39": 0.125,
                "20-29": 0.30,
                "10-19": 0.20,
                "00-09": 0.085
            },
            "sex": {
                "male": 0.505,
                "female": 0.495
            }
        },
        "mortalities": {
            "age": {
                "80+": 0.4840,
                "70-79": 0.2317,
                "60-69": 0.1592,
                "50-59": 0.0817,
                "40-49": 0.0292,
                "30-39": 0.0111,
                "20-29": 0.0037,
                "10-19": 0.0003,
                "00-09": 0.0001
            },
            "sex": {
                "male": 0.618,
                "female": 0.382
            }
        },
        "value": {
            "private": {
                "susceptible": 1.0,
                "exposed": 1.0,
                "asymptomatic": 1.0,
                "sympdetected": -0.2,
                "asympdetected": -0.2,
                "severe": -5.0,
                "recovered": 0.8,
                "deceased": 0
            },
            "public": {
                "susceptible": 10.0,
                "exposed": 10.0,
                "asymptomatic": -5.0,
                "sympdetected": -1.0,
                "asympdetected": -0.2,
                "severe": -5.0,
                "recovered": 5.0,
                "deceased": -5
            },
            "test_cost": 200,
            "alpha_private": 1.0,
            "alpha_public": 1.0
        },
        "policies": {
            "isolation": {
                "proportion_isolated": 0.45,
                "day_start_isolation": 0,
                "days_isolation_lasts": 117,
                "prob_isolation_effective": 0.8,
                "after_isolation": 0.45,
            },
            "distancing": {
                "social_distance": 1.89,
                "day_distancing_start": 16,
                "days_distancing_lasts": 365
            },
            "testing": {
                "proportion_detected": 0.25,
                "day_testing_start": 130,
                "days_testing_lasts": 7,
                "tracing": True
            },
            "tracing" :{
                "day_tracing_start": 0,
                "days_tracing_lasts": 365
            },
            "massingress": {
                "new_agent_proportion": 0.3,
                "new_agent_start": 116,
                "new_agent_lasts": 14,
                "new_agent_age_mean": 2,
                "new_agent_prop_infected": 0.02
            }
        },
        "epidemiology": {
            "num_agents": 1000,
            "width": 190,
            "height": 225,
            "repscaling": 100,
            "kmob": 0.4781,
            "rate_inbound": 0.0002,
            "prop_initial_infected": 0.001,
            "avg_incubation_time": 6,
            "avg_recovery_time": 10,
            "proportion_asymptomatic": 0.35,
            "proportion_severe": 0.05,
            "prob_contagion": 0.004,
            "proportion_beds_pop": 0.001
        }
    },
    "ensemble": {
        # "steps": 14688,
        "steps": 7000,
        "runs": 30
    },
    "output": {
        "prefix": "outcomes/cu-25-nisol.csv"
    }
}

from datetime import datetime
tick = datetime.now()
df = hello_covid(data)
tock = datetime.now()
run_time = (tock-tick).seconds/60
steps = data['ensemble']['steps']
print(f"{steps} steps took {run_time} minutes for a rate of {steps/run_time}")
