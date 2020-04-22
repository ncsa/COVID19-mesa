# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from datacollection import DataCollector
from scipy.stats import poisson, bernoulli
from enum import Enum
import numpy as np
import sys


class Stage(Enum):
    SUSCEPTIBLE = 1
    INCUBATING = 2
    ASYMPTOMATIC = 3
    SYMPDETECTED = 4
    ASYMPDETECTED = 5
    SEVERE = 6
    RECOVERED = 7
    DECEASED = 8


class AgeGroup(Enum):
    C00to09 = 0
    C10to19 = 1
    C20to29 = 2
    C30to39 = 3
    C40to49 = 4
    C50to59 = 5
    C60to69 = 6
    C70to79 = 7
    C80toXX = 8


class SexGroup(Enum):
    MALE = 1
    FEMALE = 2


class LockGroup(Enum):
    LOCKED = 1
    MOBILE = 2


class ValueGroup(Enum):
    PERSONAL = 1
    PUBLIC = 2 


class CovidAgent(Agent):
    """ An agent representing a potential covid case"""
    
    def __init__(self, unique_id, ageg, sexg, mort, distancing, model):
        super().__init__(unique_id, model)
        self.stage = Stage.SUSCEPTIBLE
        self.age_group = ageg
        self.sex_group = sexg
        # These are fixed values associated with properties of individuals
        self.incubation_time = poisson.rvs(model.avg_incubation)
        self.dwelling_time = poisson.rvs(model.avg_dwell)
        self.recovery_time = poisson.rvs(model.avg_recovery)
        self.prob_contagion = self.model.prob_contagion_base
        # Mortality in vulnerable population appears to be around day 2-3
        self.mortality_value = 5*mort/model.avg_recovery
        # Severity appears to appear after day 5
        self.severity_value = 3*model.prob_severe/model.avg_recovery
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
        self.count_value_tested = False
        # Economic assumptions
        self.cummul_private_value = 0
        self.cummul_public_value = 0
        # Employment
        self.employed = True
        
    def alive(self):
        print(f'{self.unique_id} {self.age_group} {self.sex_group} is alive')

    def is_contagious(self):
        return (self.stage == Stage.INCUBATING) or (self.stage == Stage.ASYMPTOMATIC)

    def dmult(self):
        # In this function, we simulate aerosol effects exhibited by droplets due to
        # both the contributions of a) a minimum distance with certainty of infection
        # and a the decreasing bioavailability of droplets, modeled as a sigmoid function.
        # Units are in meters. We assume that after 1.5 meter bioavailability decreases as a
        # sigmoid. This case supposses infrequent sneezing, but usual saliva droplets when
        # masks are not in use. A multiplier of k = 10 is used as a sharpening parameter
        # of the distribution and must be further callibrated.
        mult = 1.0

        if self.model.distancing >= 1.5:
            k = 10
            mult = 1.0 - (1.0 / (1.0 + np.exp(k*(-(self.model.distancing - 1.5) + 0.5))))

        return mult

    # In this function, we count effective interactants
    def interactants(self):
        count = 0

        if (self.stage != Stage.DECEASED) and (self.stage != Stage.RECOVERED):
            for agent in self.model.grid.get_cell_list_contents([self.pos]):
                if agent.unique_id != self.unique_id:
                    if not(agent.isolated) or self.isolated_but_inefficient:
                        count = count + 1

        return count

    def step(self):
        # We compute unemployment in general as a probability of 0.00018 per day.
        # In 60 days, this is equivalent to a probability of 1% unemployment filings.
        if self.employed:
            if self.isolated:
                if bernoulli.rvs(32*0.00018/self.model.dwell_15_day):
                    self.employed = False
            else:
                if bernoulli.rvs(8*0.00018/self.model.dwell_15_day):
                    self.employed = False

        # We also compute the probability of re-employment, which is at least ten times
        # as smaller in a crisis.
        if not(self.employed):
            if bernoulli.rvs(0.000018/self.model.dwell_15_day):
                self.employed = True

         # Social distancing
        if not(self.in_distancing) and (self.astep >= self.model.distancing_start):
            self.prob_contagion = self.dmult() * self.model.prob_contagion_base
            self.in_distancing = True

        if self.in_distancing and (self.astep >= self.model.distancing_end):
            self.prob_contagion = self.model.prob_contagion_base
            self.in_distancing = False

        # Testing
        if not(self.in_testing) and (self.astep >= self.model.testing_start):
            self.test_chance = self.model.testing_rate
            self.in_testing = True

        if self.in_testing and (self.astep >= self.model.testing_end):
            self.test_chance = 0
            self.in_testing = False

        # Self isolation is tricker. We only isolate susceptibles, incubating and asymptomatics
        if not(self.in_isolation) and (self.astep >= self.model.isolation_start):
            if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.INCUBATING) or \
                (self.stage == Stage.ASYMPTOMATIC):
                if bool(bernoulli.rvs(self.model.isolation_rate)):
                    self.isolated = True
                else:
                    self.isolated = False
                self.in_isolation = True
                
        # Using a similar logic, we remove isolation for all relevant agents still locked
        if self.in_isolation and (self.astep >= self.model.isolation_end):
            if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.INCUBATING) or \
                (self.stage == Stage.ASYMPTOMATIC):
                self.isolated = False
                self.in_isolation = False

        if self.stage == Stage.SUSCEPTIBLE:
            # Important: infected people drive the spread, not
            # the number of healthy ones

            # If testing is available and the date is reached, test
            # Testing of a healthy person should maintain them as
            # still susceptible.
            # We take care of testing probability at the top level step
            # routine to avoid this repeated computation
            if not(self.count_value_tested) and bernoulli.rvs(self.test_chance):
                self.count_value_tested = True
            # First opportunity to get infected: contact with others
            # in near proximity
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            infected_contact = False

            # Isolated people should only be contagious if they do not follow proper
            # shelter-at-home measures
            for c in cellmates:
                    if c.is_contagious():
                        if self.isolated and bernoulli.rvs(1 - self.model.prob_isolation_effective):
                            self.isolated_but_inefficient = True
                            infected_contact = True
                            break
                        else:
                            infected_contact = True
                            break        
            
            # Value is computed before infected stage happens
            isolation_private_divider = 1
            isolation_public_divider = 1

            if self.employed:
                if self.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01


                self.cummul_private_value = self.cummul_private_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.SUSCEPTIBLE])*isolation_private_divider
                self.cummul_public_value = self.cummul_public_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SUSCEPTIBLE])*isolation_public_divider
            else:
                self.cummul_private_value = self.cummul_private_value + 0
                self.cummul_public_value = self.cummul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SUSCEPTIBLE]

            if infected_contact:
                if self.isolated:
                    if bernoulli.rvs(self.prob_contagion) and \
                        not(bernoulli.rvs(self.model.prob_isolation_effective)):
                        self.stage = Stage.INCUBATING
                else:
                    if bernoulli.rvs(self.prob_contagion):
                        self.stage = Stage.INCUBATING

            # Second opportunity to get infected: residual droplets in places
            # TODO

            if not(self.isolated):
                self.move()
        elif self.stage == Stage.INCUBATING:
            # Susceptible patients only move and spread the disease.
            # If the incubation time is reached, it is immediately 
            # considered as detected since it is severe enough.

            # We compute the private value as usual
            cellmates = self.model.grid.get_cell_list_contents([self.pos])

            isolation_private_divider = 1
            isolation_public_divider = 1

            if self.employed:
                if self.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01
                
                self.cummul_private_value = self.cummul_private_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.INCUBATING])*isolation_private_divider
                self.cummul_public_value = self.cummul_public_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.INCUBATING])*isolation_public_divider
            else:
                self.cummul_private_value = self.cummul_private_value + 0
                self.cummul_public_value = self.cummul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.INCUBATING]

            # If testing is available and the date is reached, test
            if not(self.count_value_tested) and bernoulli.rvs(self.test_chance):
                if bernoulli.rvs(self.model.prob_asymptomatic):
                    self.stage = Stage.ASYMPDETECTED
                else:
                    self.stage = Stage.SYMPDETECTED
                
                self.count_value_tested = True
            else:
                if self.curr_incubation < self.incubation_time:
                    self.curr_incubation = self.curr_incubation + 1
                    if not(self.isolated):
                        self.move()
                else:
                    if bernoulli.rvs(self.model.prob_asymptomatic):
                        self.stage = Stage.ASYMPTOMATIC
                    else:
                        self.stage = Stage.SYMPDETECTED
        elif self.stage == Stage.ASYMPTOMATIC:
            # Asymptomayic patients only roam around, spreading the
            # disease, ASYMPDETECTEDimmune system
            cellmates = self.model.grid.get_cell_list_contents([self.pos])

            isolation_private_divider = 1
            isolation_public_divider = 1

            if self.employed:
                if self.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01
                
                    self.cummul_private_value = self.cummul_private_value + \
                        ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.ASYMPTOMATIC])*isolation_private_divider
                    self.cummul_public_value = self.cummul_public_value + \
                        ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPTOMATIC])*isolation_public_divider
                else:
                    self.cummul_private_value = self.cummul_private_value + 0
                    self.cummul_public_value = self.cummul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPTOMATIC]

            if not(self.count_value_tested) and bernoulli.rvs(self.test_chance):
                self.stage = Stage.ASYMPDETECTED
                self.count_value_tested = True
            else:
                if self.curr_recovery < self.recovery_time:
                    if not(self.isolated):
                        self.move()
                else:
                    self.stage = Stage.RECOVERED
        elif self.stage == Stage.SYMPDETECTED:
            # Once a symptomatic patient has been detected, it does not move and starts
            # the road to severity, recovery or death
            self.isolated = True
            
            self.cummul_private_value = self.cummul_private_value + \
                self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.SYMPDETECTED]
            self.cummul_public_value = self.cummul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SYMPDETECTED]

            if self.curr_incubation + self.curr_recovery < self.incubation_time + self.recovery_time:
                # Not recovered yet, may pass away depending on prob.
                if bernoulli.rvs(self.mortality_value):
                    self.stage = Stage.DECEASED
                else:
                    self.curr_recovery = self.curr_recovery + 1

                    if bernoulli.rvs(self.severity_value):
                        self.stage = Stage.SEVERE
            else:
                self.stage = Stage.RECOVERED
        elif self.stage == Stage.ASYMPDETECTED:
            self.isolated = True

            self.cummul_private_value = self.cummul_private_value + \
                self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.ASYMPDETECTED]
            self.cummul_public_value = self.cummul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPDETECTED]

            # The road of an asymptomatic patients is similar without the prospect of death
            if self.curr_incubation + self.curr_recovery < self.incubation_time + self.recovery_time:
               self.curr_recovery = self.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
        elif self.stage == Stage.SEVERE:            
            self.cummul_private_value = self.cummul_private_value + \
                self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.SEVERE]
            self.cummul_public_value = self.cummul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SEVERE]

            # Severe patients are in ICU facilities
            if self.curr_recovery < self.recovery_time:
                # Not recovered yet, may pass away depending on prob.
                if bernoulli.rvs(self.mortality_value):
                    self.stage = Stage.DECEASED
                else:
                    self.curr_recovery = self.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
        elif self.stage == Stage.RECOVERED:
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            
            if self.employed:
                isolation_private_divider = 1
                isolation_public_divider = 1

                if self.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01

                self.cummul_private_value = self.cummul_private_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.RECOVERED])*isolation_private_divider
                self.cummul_public_value = self.cummul_public_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.RECOVERED])*isolation_public_divider
            else:
                self.cummul_private_value = self.cummul_private_value + 0
                self.cummul_public_value = self.cummul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.RECOVERED]

            # A recovered agent can now move freely within the grid again
            self.curr_recovery = 0
            self.isolated = False
            self.isolated_but_inefficient = False
            self.move()
        elif self.stage == Stage.DECEASED:
            self.cummul_private_value = self.cummul_private_value + \
                self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.DECEASED]
            self.cummul_public_value = self.cummul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.DECEASED]
        else:
            # If we are here, there is a problem 
            sys.exit("Unknown stage: aborting.")

        self.astep = self.astep + 1

    def move(self):
        # If dwelling has not been exhausted, do not move
        if self.curr_dwelling > 0:
            self.curr_dwelling = self.curr_dwelling - 1

        # If dwelling has been exhausted, move and replenish the dwell
        else:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            new_position = self.random.choice(possible_steps)

            self.model.grid.move_agent(self, new_position)
            self.curr_dwelling = poisson.rvs(self.model.avg_dwell)

def compute_susceptible(model):
    return count_type(model, Stage.SUSCEPTIBLE)/model.num_agents

def compute_incubating(model):
    return count_type(model, Stage.INCUBATING)/model.num_agents

def compute_asymptomatic(model):
    return count_type(model, Stage.ASYMPTOMATIC)/model.num_agents

def compute_symptdetected(model):
    return count_type(model, Stage.SYMPDETECTED)/model.num_agents

def compute_asymptdetected(model):
    return count_type(model, Stage.ASYMPDETECTED)/model.num_agents

def compute_severe(model):
    return count_type(model, Stage.SEVERE)/model.num_agents

def compute_recovered(model):
    return count_type(model, Stage.RECOVERED)/model.num_agents

def compute_deceased(model):
    return count_type(model, Stage.DECEASED)/model.num_agents

def count_type(model, stage):
    count = 0

    for agent in model.schedule.agents:
        if agent.stage == stage:
            count = count + 1

    return count

def compute_isolated(model):
    count = 0

    for agent in model.schedule.agents:
        if agent.isolated:
            count = count + 1

    return count/model.num_agents

def compute_employed(model):
    count = 0

    for agent in model.schedule.agents:
        if agent.employed:
            count = count + 1

    return count/model.num_agents

def compute_unemployed(model):
    count = 0

    for agent in model.schedule.agents:
        if not(agent.employed):
            count = count + 1

    return count/model.num_agents

def compute_contacts(model):
    count = 0

    for agent in model.schedule.agents:
        count = count + agent.interactants()

    return count/len(model.schedule.agents)

def compute_stepno(model):
    return model.stepno

def compute_commul_private_value(model):
    value = 0

    for agent in model.schedule.agents:
        value = value + agent.cummul_private_value

    return np.power(value, model.alpha_private)/model.num_agents

def compute_commul_public_value(model):
    value = 0

    for agent in model.schedule.agents:
        value = value + agent.cummul_public_value

    return np.power(value, model.alpha_public)

def compute_commul_testing_cost(model):
    tested = 0

    for agent in model.schedule.agents:
        if agent.count_value_tested:
            tested = tested + 1

    return tested * model.test_cost

def compute_eff_reprod_number(model):
    prob_contagion = 0.0

    for agent in model.schedule.agents:
        if (agent.stage == Stage.SUSCEPTIBLE) or (agent.stage == Stage.INCUBATING) or \
            (agent.stage == Stage.ASYMPTOMATIC):
            prob_contagion = agent.prob_contagion
            break

    avg_contacts = compute_contacts(model)
    return prob_contagion * avg_contacts * model.avg_incubation


class CovidModel(Model):
    """ A model to describe parameters relevant to COVID-19"""
    def __init__(self, num_agents, width, height, age_mortality, sex_mortality, age_distribution, sex_distribution, 
                 proportion_asymptomatic, proportion_severe, avg_incubation_time, avg_recovery_time,
                 prob_contagion, proportion_isolated, day_start_isolation, days_isolation_lasts, prob_isolation_effective,
                 social_distance, day_distancing_start, days_distancing_lasts, proportion_detected, day_testing_start, days_testing_lasts,
                 stage_value_matrix, test_cost, alpha_private, alpha_public, dummy=0):
        self.running = True
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.age_mortality = age_mortality
        self.sex_mortality = sex_mortality
        self.age_distribution = age_distribution
        self.sex_distribution = sex_distribution
        self.stage_value_dist = stage_value_matrix
        self.test_cost = test_cost
        self.stepno = 0
        self.alpha_private = alpha_private
        self.alpha_public = alpha_public

        # Number of 15 minute dwelling times per day
        self.dwell_15_day = 96

        # Average dwelling units
        self.avg_dwell = 4

        # The average incubation period is 5 days, which can be changed
        self.avg_incubation = int(round(avg_incubation_time * self.dwell_15_day))

        # Probability of contagion after exposure in the same cell
        # Presupposes a person centered on a 1.8 meter radius square.
        # We use a proxy value to account for social distancing
        self.prob_contagion_base = prob_contagion

        # Probability of contagion due to residual droplets
        self.prob_contagion_places = 0.001

        # Probability of being asymptomatic, contagious
        # and only detectable by testing
        self.prob_asymptomatic = proportion_asymptomatic

        # Average recovery time
        self.avg_recovery = avg_recovery_time * self.dwell_15_day

        # Proportion of detection. We use the rate as reference and
        # activate testing at the rate and specified dates
        self.testing_rate = proportion_detected/(days_testing_lasts  * self.dwell_15_day)
        self.testing_start = day_testing_start* self.dwell_15_day
        self.testing_end = self.testing_start + days_testing_lasts*self.dwell_15_day

        # Same for isolation rate
        self.isolation_rate = proportion_isolated
        self.isolation_start = day_start_isolation*self.dwell_15_day
        self.isolation_end = self.isolation_start + days_isolation_lasts*self.dwell_15_day
        self.prob_isolation_effective = prob_isolation_effective

        # Same for social distancing
        self.distancing = social_distance
        self.distancing_start = day_distancing_start*self.dwell_15_day
        self.distancing_end = self.distancing_start + days_distancing_lasts*self.dwell_15_day

        # Probability of severity
        self.prob_severe = proportion_severe

        # Create agents
        i = 0

        for ag in self.age_distribution:
            for sg in self.sex_distribution:
                r = self.age_distribution[ag]*self.sex_distribution[sg]
                num_agents = int(round(self.num_agents*r))
                mort = self.age_mortality[ag]*self.sex_mortality[sg]
                for k in range(num_agents):
                    a = CovidAgent(i, ag, sg, mort, self.distancing, self)
                    self.schedule.add(a)
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    self.grid.place_agent(a, (x,y))
                    i = i + 1
        
        self.datacollector = DataCollector(
            model_reporters = {
                "Step": compute_stepno,
                "Susceptible": compute_susceptible,
                "Incubating": compute_incubating,
                "Asymptomatic": compute_asymptomatic,
                "SymptQuarantined": compute_symptdetected,
                "AsymptQuarantined": compute_asymptdetected,
                "Severe": compute_severe,
                "Recovered": compute_recovered,
                "Deceased": compute_deceased,
                "Isolated": compute_isolated,
                "CummulPrivValue": compute_commul_private_value,
                "CummulPublValue": compute_commul_public_value,
                "CummulTestCost": compute_commul_testing_cost,
                "Contacts": compute_contacts,
                "Rt": compute_eff_reprod_number,
                "Employed": compute_employed,
                "Unemployed": compute_unemployed
            },
            agent_reporters = {
                "Position": "pos",
                "Dwelling": "curr_dwelling",
                "Incubation": "curr_incubation",
                "Recovert": "curr_recovery"
            }
        )

        # Final step: infect a random agent that is not isolated
        first_infected = self.random.choice(self.schedule.agents)
        
        while first_infected.isolated:
            first_infected = self.random.choice(self.schedule.agents)
        
        first_infected.stage = Stage.INCUBATING
   
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.stepno = self.stepno + 1
