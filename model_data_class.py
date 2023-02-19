from dataclasses import dataclass

# the data class for CovidModel
@dataclass
class ModelDataClass:
    age_mortality: dict()
    sex_mortality: dict()
    age_distribution: dict()
    sex_distribution: dict()
    stage_value_dist: dict()
    test_cost: int
    alpha_private: float
    alpha_public: float
    fully_vaccinated_count: int
    prop_initial_infected: float
    generally_infected: int
    cumul_vaccine_cost: int
    cumul_test_cost: int
    total_costs: int
    vaccination_chance: float
    vaccination_stage: int
    vaccine_cost: int
    day_vaccination_begin: int
    day_vaccination_end: int
    effective_period: int
    effectiveness: float
    distribution_rate: int
    vaccine_count: int
    vaccinated_count: int
    vaccinated_percent: float
    vaccine_dosage: int
    effectiveness_per_dosage: float
    variant_data_list: dict()
    agent_parameter_names: list()
    dwell_15_day: int
    avg_dwell: int
    avg_incubation: int
    repscaling: int
    prob_contagion_base: float
    kmob: float
    rate_inbound: float
    prob_contagion_places: float
    prob_asymptomatic: float
    avg_recovery: int
    testing_rate: float
    testing_start: int
    testing_end: int
    tracing_start: int
    tracing_end: int
    tracing_now: bool
    isolation_rate: float
    isolation_start: int
    isolation_end: int
    after_isolation: int
    prob_isolation_effective: float
    distancing: float
    distancing_start: int
    distancing_end: int
    new_agent_num: int
    new_agent_start: int
    new_agent_end: int
    new_agent_age_mean: int
    new_agent_prop_infected: float
    vaccination_start: int
    vaccination_end: int
    vaccination_now: bool
    variant_start_times: dict()
    variant_start: dict()
    prob_severe: float
    max_bed_available: int
    bed_count: int
    # location types
    location_types: dict()
    locations: dict()

    


       