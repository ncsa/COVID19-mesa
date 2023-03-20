from dataclasses import dataclass
import sys


# the data class for CovidModel
@dataclass
class ModelDataClass:
    # Population data
    age_mortality: dict()
    sex_mortality: dict()
    age_distribution: dict()
    sex_distribution: dict()
    # Econometric model
    stage_value_dist: dict()
    alpha_private: float
    alpha_public: float
    # Vaccination related data
    vaccination_start: int = sys.maxsize
    vaccination_end: int = sys.maxsize
    vaccination_now: bool = False
    cumul_vaccine_cost: int = 0
    cumul_test_cost: int = 0
    total_costs: int = 0
    vaccination_chance: float = 0.0
    vaccination_stage: int
    vaccine_cost: int
    fully_vaccinated_count: int
    effective_period: int
    effectiveness: float
    vaccine_count: int
    vaccinated_count: int
    vaccinated_percent: float
    vaccine_dosage: int
    effectiveness_per_dosage: float
    distribution_rate: int
    # Variant data
    variant_data_list: dict()
    agent_parameter_names: list()
    variant_start_times: dict()
    variant_start: dict()
    # Testing
    test_cost: int
    testing_rate: float
    testing_start: int
    testing_end: int
    tracing_start: int
    tracing_end: int
    tracing_now: bool
    # Isolation
    isolation_rate: float
    isolation_start: int
    isolation_end: int
    prob_isolation_effective: float
    # Distancing
    distancing: float
    distancing_start: int
    distancing_end: int
    # Massive ingress
    new_agent_num: int
    new_agent_start: int
    new_agent_end: int
    new_agent_age_mean: int
    new_agent_prop_infected: float
    # Epidemic parameters
    dwell_15_day: int
    avg_dwell: int
    avg_incubation: int
    repscaling: int
    prob_contagion_base: float
    kmob: float
    rate_inbound: float
    prob_contagion_places: float
    prop_initial_infected: float
    generally_infected: int
    prob_asymptomatic: float
    avg_recovery: int
    prob_severe: float
    max_bed_available: int
    bed_count: int

    


       