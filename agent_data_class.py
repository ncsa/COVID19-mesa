from scipy.stats import poisson, bernoulli

# The agent class contains all the parameters for an agent
class AgentDataClass:
    def __init__(self, model, is_checkpoint, params):
        # start from time 0
        if not is_checkpoint:
            self.age_group = params[1]
            self.sex_group = params[2]
            self.vaccine_willingness = bernoulli.rvs(model.model_data.vaccinated_percent)
            # These are fixed values associated with properties of individuals
            self.incubation_time = poisson.rvs(model.model_data.avg_incubation)
            self.dwelling_time = poisson.rvs(model.model_data.avg_dwell)
            self.recovery_time = poisson.rvs(model.model_data.avg_recovery)
            self.prob_contagion = model.model_data.prob_contagion_base
            # Mortality in vulnerable population appears to be around day 2-3
            self.mortality_value = params[3]
            # Severity appears to appear after day 5
            self.severity_value = model.model_data.prob_severe/(model.model_data.dwell_15_day*self.recovery_time)
            self.curr_dwelling = 0
            self.curr_incubation = 0
            self.curr_recovery = 0
            self.curr_asymptomatic = 0
            # Isolation measures are set at the model step level
            self.isolated = False
            self.isolated_but_inefficient = False
            # Contagion probability is local
            self.test_chance = 0
            # Horrible hack for isolation step
            self.in_isolation = False
            self.in_distancing = False
            self.in_testing = False
            self.astep = 0
            self.tested = False
            self.occupying_bed = False
            # Economic assumptions
            self.cumul_private_value = 0
            self.cumul_public_value = 0
            # Employment
            self.employed = True
            # Contact tracing: this is only available for symptomatic patients
            self.tested_traced = False
            # All agents 
            self.contacts = set()
            # We assume it takes two full days
            self.tracing_delay = 2*model.model_data.dwell_15_day
            self.tracing_counter = 0
            #vaccination variables
            self.vaccinated = False
            self.safetymultiplier = 1
            self.current_effectiveness = 0
            self.vaccination_day = 0
            self.vaccine_count = 0
            self.dosage_eligible = True
            self.fully_vaccinated = False
            self.variant = "Standard"
            self.variant_immune = {}
            for variant in model.model_data.variant_data_list:
                self.variant_immune[variant] = False

        # start from an existing file
        else:
            self.age_group = params[2]
            self.sex_group = params[3]
            self.vaccine_willingness = params[4]
            # These are fixed values associated with properties of individuals
            self.incubation_time = params[5]
            self.dwelling_time = params[6]
            self.recovery_time = params[7]
            self.prob_contagion = params[8]
            # Mortality in vulnerable population appears to be around day 2-3
            self.mortality_value = params[9]
            # Severity appears to appear after day 5
            self.severity_value = params[10]
            self.curr_dwelling = params[11]
            self.curr_incubation = params[12]
            self.curr_recovery = params[13]
            self.curr_asymptomatic = params[14]
            # Isolation measures are set at the model step level
            self.isolated = params[15]
            self.isolated_but_inefficient = params[16]
            # Contagion probability is local
            self.test_chance = params[17]
            # Horrible hack for isolation step
            self.in_isolation = params[18]
            self.in_distancing = params[19]
            self.in_testing = params[20]
            self.astep = params[21]
            self.tested = params[22]
            self.occupying_bed = params[23]
            # Economic assumptions
            self.cumul_private_value = params[24]
            self.cumul_public_value = params[25]
            # Employment
            self.employed = params[26]
            # Contact tracing: this is only available for symptomatic patients
            self.tested_traced = params[27]
            # All agents
            self.contacts = params[28]
            # We assume it takes two full days
            self.tracing_delay = params[29]
            self.tracing_counter = params[30]
            # vaccination variables
            self.vaccinated = params[31]
            self.safetymultiplier = params[32]
            self.current_effectiveness = params[33]
            self.vaccination_day = params[34]
            self.vaccine_count = params[35]
            self.dosage_eligible = params[36]
            self.fully_vaccinated =  params[37]
            self.variant = params[38]
            self.variant_immune = params[39]