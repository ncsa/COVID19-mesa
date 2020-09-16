import json
import time
import sys
import math
import os.path
from funcx.sdk.client import FuncXClient
from datetime import datetime
# ENDPOINT = "b65c5efb-9772-44d3-ac7f-1bb6c820cea4"  # Radiant
# ENDPOINT = 'c00a0169-934b-40de-8087-2eebe8770052'  # Boneyard
from globus_sdk import GlobusAPIError

ENDPOINT = '7a5ce47f-7352-4468-9a8a-73c3233c91fe'  # River
NUM_RUNS = 30

fxc = FuncXClient()


def hello_covid(data):
    from batchrunner_local import FixedBatchRunner
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


def get_task_status(batch_uuid):
    try:
        status_list = fxc.get_batch_status(batch_uuid)
        return status_list
    except GlobusAPIError:
        print("Error connecting to funcX server. Will retry in 120 seconds")
        return None


covid_function = fxc.register_function(hello_covid)
print(covid_function)

if len(sys.argv) != 2:
    print("Usage: ensemble_runner.py <<scenario file>>")
    sys.exit(-1)

scenario_file = sys.argv[1]
scenario = os.path.basename(scenario_file)
run_id = f'{scenario}-{math.floor(datetime.now().timestamp())}'
output_dir = os.path.join('outcomes', run_id)
os.mkdir(output_dir)

# Read JSON file
with open(scenario_file) as f:
    data = json.load(f)

    # data["ensemble"]["steps"] = 25
    data["model"]["policies"]["isolation"]["after_isolation"] = 0.0

    batch = fxc.create_batch()
    for i in range(NUM_RUNS):
        batch.add(data, endpoint_id=ENDPOINT, function_id=covid_function)

    batch_res = fxc.batch_run(batch)
    print(batch_res)
    done = False
    while not done:
        status_list = get_task_status(batch_res)

        if status_list:
            complete_count = sum([1 for t in status_list.keys() if t in status_list and status_list[t]['pending']=="False"])
            print(complete_count)
        else:
            complete_count = None

        if complete_count == NUM_RUNS:
            for task in status_list.keys():
                result_df = status_list[task]['result']
                result_df.to_csv(os.path.join(output_dir, f'{task}.csv'))
            done = True
        else:
            time.sleep(120)

