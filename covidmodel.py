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
    INFECTED = 2
    DETECTED = 3
    RECOVERED = 4
    DECEASED = 5


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

class CovidAgent(Agent):
    """ An agent representing a potential covid case"""
    
    def __init__(self, unique_id, ageg, sexg, mort, distancing, model):
        super().__init__(unique_id, model)
        self.stage = Stage.SUSCEPTIBLE
        self.age_group = ageg
        self.sex_group = sexg
        # These are fixed values associated with properties of individuals
        self.incubation_time = poisson(model.avg_incubation).rvs()
        self.dwelling_time = poisson(model.avg_dwell).rvs()
        self.recovery_time = poisson(model.avg_recovery).rvs()
        # These are random Bernoulli variables, not values!
        self.infection = bernoulli(model.prob_contagion)
        self.infect_place = bernoulli(model.prob_contagion_places)
        self.mortality = bernoulli(mort/model.avg_recovery)
        self.detection = bernoulli(model.prob_detection)
        self._model = model
        self.curr_dwelling = 0
        self.curr_incubation = 0
        self.curr_recovery = 0
        self.distancing = distancing
        self.locked = False

    def alive(self):
        print(f'{self.unique_id} {self.age_group} {self.sex_group} {self.mortality} is alive')

    def is_infected(self):
        return self.stage == Stage.INFECTED

    def step(self):
        if self.stage == Stage.SUSCEPTIBLE:
            # Important: infected people drive the spread, not
            # the number of healthy ones

            # First opportunity to get infected: contact with others
            # in near proximity
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            infected_contact = False

            for c in cellmates:
                if c.is_infected():
                    infected_contact = True
                    break

            if infected_contact:
                if self.infection.rvs():
                    self.stage = Stage.INFECTED

            # Second opportunity to get infected: residual droplets in places
            # TODO

            if not(self.locked):
                self.move()
        elif self.stage == Stage.INFECTED:
            # Susceptible patients only move and spread the disease.
            # If the incubation time is reached, it is immediately 
            # considered as detected since it is severe enough.
            if self.curr_incubation < self.incubation_time:
                self.curr_incubation = self.curr_incubation + 1
                if not(self.locked):
                    self.move()
            else:
                self.stage = Stage.DETECTED
        elif self.stage == Stage.DETECTED:
            # Once a patient has been detected, it does not move and starts
            # the road to recovery or death
            #
            # Limitation: our model fails to capture severity per day
            # in an ICU, this needs to be included.
            if self.curr_recovery < self.recovery_time:
                # Not recovered yet, may pass away depending on prob.
                if self.mortality.rvs():
                    self.stage = Stage.DECEASED
                else:
                    self.curr_recovery = self.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
        elif self.stage == Stage.RECOVERED:
            # A recovered agent can now move freely within the grid again
            self.curr_recovery = 0
            if not(self.locked):
                self.move()
        elif self.stage == Stage.DECEASED:
            # Do nothing. Do not move or do any action.
            pass
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
            self.curr_dwelling = poisson(self._model.avg_dwell).rvs()

def compute_susceptible(model):
    return count_type(model, Stage.SUSCEPTIBLE)

def compute_infected(model):
    return count_type(model, Stage.INFECTED)

def compute_detected(model):
    return count_type(model, Stage.DETECTED)

def compute_recovered(model):
    return count_type(model, Stage.RECOVERED)

def compute_deceased(model):
    return count_type(model, Stage.DECEASED)

def count_type(model, stage):
    count = 0

    for agent in model.schedule.agents:
        if agent.stage == stage:
            count = count + 1

    return count

class CovidModel(Model):
    """ A model to describe parameters relevant to COVID-19"""
    def __init__(self, N, width, height, distancing, amort, 
                 smort, adist, sdist, plock, pcont, pdet):
        self.running = True
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.age_mortality = amort
        self.sex_mortality = smort
        self.age_distribution = adist
        self.sex_distribution = sdist

        # Number of 15 minute dwelling times per day
        self._dwell_15_day = 96

        # Average dwelling units
        self.avg_dwell = 4

        # The average incubation period is 5 days, which can be changed
        self.avg_incubation = 5 * self._dwell_15_day

        # Probability of contagion after exposure in the same cell
        # Presupposes a person centered on a 1.8 meter radius square
        self.prob_contagion = pcont

        # Probability of contagion due to residual droplets
        self.prob_contagion_places = 0.001

        # Average recovery time
        self.avg_recovery = 15 * self._dwell_15_day

        # Probsbility of detection
        self.prob_detection = pdet

        # Probability of lockdown
        self.prob_lock = plock

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
                "Susceptible": compute_susceptible,
                "Infected": compute_infected,
                "Detected": compute_detected,
                "Recovered": compute_recovered,
                "Deceased": compute_deceased
            },
            agent_reporters = {
                "Position": "pos",
                "Dwelling": "curr_dwelling",
                "Incubation": "curr_incubation",
                "Recovert": "curr_recovery"
            }
        )

        # Now, setup all agents according to lock down rules
        n_ags = len(self.schedule.agents)
        n_lock = int(round(n_ags * self.prob_lock))
        i_ag = 0

        for a in self.schedule.agents:
            if i_ag < n_lock:
                a.locked = True
                continue
            else:
                break

        # Final step: infect a random agent that is not locked
        
        first_infected = self.random.choice(self.schedule.agents)
        
        while first_infected.locked:
            first_infected = self.random.choice(self.schedule.agents)
        
        print(first_infected.unique_id)
        first_infected.stage = Stage.INFECTED
   
    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
