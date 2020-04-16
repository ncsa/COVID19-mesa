# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
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
        # self.infect_place = bernoulli(model.prob_contagion_places)
        # Mortality in vulnerable population appears to be around day 2-3
        self.mortality_value = 5*mort/model.avg_recovery
        # Number of days since detection applied
        self.days_detection = model.days_detection
        # Severity appears to appear after day 5
        self.severity_value = 3*model.prob_severe/model.avg_recovery
        self.curr_dwelling = 0
        self.curr_incubation = 0
        self.curr_recovery = 0
        self.curr_asymptomatic = 0
        self.distancing = distancing
        self.locked = bool(bernoulli(self.model.prob_lock).rvs())
        self.astep = 0
        self.count_value_tested = False
        self.cummul_personal_value = 0
        self.cummul_public_value = 0

    def alive(self):
        print(f'{self.unique_id} {self.age_group} {self.sex_group} is alive')

    def is_contagious(self):
        return (self.stage == Stage.INCUBATING) or (self.stage == Stage.ASYMPTOMATIC)

    def interactants(self):
        return len(self.model.grid.get_cell_list_contents([self.pos]))

    def step(self):
        self.astep = self.astep + 1

        if self.stage == Stage.SUSCEPTIBLE:
            # Important: infected people drive the spread, not
            # the number of healthy ones

            # If testing is available and the date is reached, test
            # Testing of a healthy person should maintain them as
            # still susceptible
            if (self.astep >= self.model.days_detection) and \
                (bernoulli.rvs(self.model.prob_detection)):
                self.count_value_tested = True
            # First opportunity to get infected: contact with others
            # in near proximity
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            infected_contact = False

            for c in cellmates:
                    if c.is_contagious():
                        infected_contact = True
                        break        
            
            # Value is computed before infected stage happens
            self.cummul_personal_value = self.cummul_personal_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.SUSCEPTIBLE])
            self.cummul_public_value = self.cummul_public_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SUSCEPTIBLE])

            if infected_contact:
                if self.locked:
                    if bernoulli.rvs(self.model.prob_contagion) and \
                        not(bernoulli.rvs(self.model.prob_lock_effective)):
                        self.stage = Stage.INCUBATING
                else:
                    if bernoulli.rvs(self.model.prob_contagion):
                        self.stage = Stage.INCUBATING

            # Second opportunity to get infected: residual droplets in places
            # TODO

            if not(self.locked):
                self.move()
        elif self.stage == Stage.INCUBATING:
            # Susceptible patients only move and spread the disease.
            # If the incubation time is reached, it is immediately 
            # considered as detected since it is severe enough.

            # We compute the personal value as usual
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            
            self.cummul_personal_value = self.cummul_personal_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.INCUBATING])
            self.cummul_public_value = self.cummul_public_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.INCUBATING])

            # If testing is available and the date is reached, test
            if (self.astep >= self.model.days_detection) and \
                (bernoulli.rvs(self.model.prob_detection)):
                if bernoulli.rvs(self.model.prob_asymptomatic):
                    self.stage = Stage.ASYMPDETECTED
                else:
                    self.stage = Stage.SYMPDETECTED
                
                self.count_value_tested = True
            else:
                if self.curr_incubation < self.incubation_time:
                    self.curr_incubation = self.curr_incubation + 1
                    if not(self.locked):
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
            
            self.cummul_personal_value = self.cummul_personal_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.ASYMPTOMATIC])
            self.cummul_public_value = self.cummul_public_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPTOMATIC])

            if (self.astep >= self.model.days_detection) and \
                (bernoulli.rvs(self.model.prob_detection)):
                self.stage = Stage.ASYMPDETECTED
                self.count_value_tested = True
            else:
                if self.curr_recovery < self.recovery_time:
                    if not(self.locked):
                        self.move()
                else:
                    self.stage = Stage.RECOVERED
        elif self.stage == Stage.SYMPDETECTED:
            # Once a symptomatic patient has been detected, it does not move and starts
            # the road to severity, recovery or death
            self.locked = True
            
            self.cummul_personal_value = self.cummul_personal_value + \
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
            self.locked = True

            self.cummul_personal_value = self.cummul_personal_value + \
                self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.ASYMPDETECTED]
            self.cummul_public_value = self.cummul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPDETECTED]

            # The road of an asymptomatic patients is similar without the prospect of death
            if self.curr_incubation + self.curr_recovery < self.incubation_time + self.recovery_time:
               self.curr_recovery = self.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
        elif self.stage == Stage.SEVERE:            
            self.cummul_personal_value = self.cummul_personal_value + \
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
            
            self.cummul_personal_value = self.cummul_personal_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.RECOVERED])
            self.cummul_public_value = self.cummul_public_value + \
                ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.RECOVERED])

            # A recovered agent can now move freely within the grid again
            self.curr_recovery = 0
            if not(self.locked):
                self.move()
        elif self.stage == Stage.DECEASED:
            self.cummul_personal_value = self.cummul_personal_value + \
                self.model.stage_value_dist[ValueGroup.PERSONAL][Stage.DECEASED]
            self.cummul_public_value = self.cummul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.DECEASED]
        else:
            # If we are here, there is a problem 
            sys.exit("Unknown stage: aborting.")

    def move(self):
        # If dwelling has not been exhausted, do not move
        if self.curr_dwelling > 0:
            self.curr_dwelling = self.curr_dwelling - 1

        # If dwelling has been exhausted, move and replenish the dwell
        else:
            if self.distancing:
                found_pos = False

                while not(found_pos):
                    possible_steps = self.model.grid.get_neighborhood(
                        self.pos,
                        moore=True,
                        include_center=False
                    )
                    (x, y) = self.random.choice(possible_steps)
                    
                    if (len(self.model.grid.get_cell_list_contents) == 0):
                        new_position = (x, y)
                        break
                    else:
                        continue
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

def compute_locked(model):
    count = 0

    for agent in model.schedule.agents:
        if agent.locked:
            count = count + 1

    return count/model.num_agents

def compute_contacts(model):
    count = 0

    for agent in model.schedule.agents:
        count = count + agent.interactants()

    return count/len(model.schedule.agents)

def compute_stepno(model):
    return model.stepno

def compute_commul_personal_value(model):
    value = 0

    for agent in model.schedule.agents:
        value = value + agent.cummul_personal_value

    return np.power(value, model.alpha_personal)

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


class CovidModel(Model):
    """ A model to describe parameters relevant to COVID-19"""
    def __init__(self, N, width, height, distancing, pasympt, amort, smort, avinc, avrec, psev, 
                 adist, sdist, plock, peffl, pcont, pdet, ddet, dimp, stvald, tcost, aper, apub):
        self.running = True
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.age_mortality = amort
        self.sex_mortality = smort
        self.age_distribution = adist
        self.sex_distribution = sdist
        self.stage_value_dist = stvald
        self.test_cost = 0
        self.stepno = 0
        self.alpha_personal = aper
        self.alpha_public = apub

        # Number of 15 minute dwelling times per day
        self.dwell_15_day = 96

        # Average dwelling units
        self.avg_dwell = 4

        # The average incubation period is 5 days, which can be changed
        self.avg_incubation = int(round(avinc * self.dwell_15_day))

        # Days elapsed before detection in place
        self.days_detection = ddet* self.dwell_15_day

        # Probability of contagion after exposure in the same cell
        # Presupposes a person centered on a 1.8 meter radius square
        self.prob_contagion = pcont

        # Probability of contagion due to residual droplets
        self.prob_contagion_places = 0.001

        # Probability of being asymptomatic, contagious
        # and only detectable by testing
        self.prob_asymptomatic = pasympt

        # Average recovery time
        self.avg_recovery = avrec * self.dwell_15_day

        # Probsbility of detection
        self.prob_detection = pdet/(dimp  * self.dwell_15_day)

        # Probability of severity
        self.prob_severe = psev

        # Proportion in shelter at home
        self.prob_lock = plock

        # Shelter-at-home effectiveness
        self.prob_lock_effective = peffl

        # Create agents
        i = 0

        for ag in self.age_distribution:
            for sg in self.sex_distribution:
                r = self.age_distribution[ag]*self.sex_distribution[sg]
                n = int(round(self.num_agents*r))
                mort = self.age_mortality[ag]*self.sex_mortality[sg]
                for k in range(n):
                    a = CovidAgent(i, ag, sg, mort, distancing, self)
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
                "Isolated": compute_locked,
                "CummulPersValue": compute_commul_personal_value,
                "CummulPublValue": compute_commul_public_value,
                "CummulTestCost": compute_commul_testing_cost
            },
            agent_reporters = {
                "Position": "pos",
                "Dwelling": "curr_dwelling",
                "Incubation": "curr_incubation",
                "Recovert": "curr_recovery"
            }
        )

        # Final step: infect a random agent that is not locked
        first_infected = self.random.choice(self.schedule.agents)
        
        while first_infected.locked:
            first_infected = self.random.choice(self.schedule.agents)
        
        first_infected.stage = Stage.INCUBATING
   
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        self.stepno = self.stepno + 1
