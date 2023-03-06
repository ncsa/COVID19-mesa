# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
import math
from operator import mod
from sqlite3 import DatabaseError
import timeit

import mesa.batchrunner
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from datacollection import DataCollector
from scipy.stats import poisson, bernoulli
from enum import Enum
import numpy as np
import random
import sys
import psutil as psu
import timeit as time
import os
import pandas as pd
from agent_data_class import AgentDataClass
from model_data_class import ModelDataClass
import uuid
from database import Database
from policyhandler import PolicyHandler


def bernoulli_rvs(p):
    # Return a sample from a Bernoulli-distributed random source
    # We convert from a Uniform(0, 1)
    r = random.random()
    if r >= p:
        return 1
    return 0


def poisson_rvs(mu):
    p0 = math.exp(-mu)
    F = p0
    i = 0
    sample = random.random()
    while sample >= F:
        i += 1
        F += p0 * (mu ** i) / math.factorial(i)
    return i


class Stage(Enum):
    SUSCEPTIBLE = 1
    EXPOSED = 2
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


class ValueGroup(Enum):
    PRIVATE = 1
    PUBLIC = 2

class VaccinationStage(Enum):
    C00to09 = 0
    C10to19 = 1
    C20to29 = 2
    C30to39 = 3
    C40to49 = 4
    C50to59 = 5
    C60to69 = 6
    C70to79 = 7
    C80toXX = 8



class CovidAgent(Agent):
    """ An agent representing a potential covid case"""
    
    def __init__(self, unique_id, ageg, sexg, mort, model):
        super().__init__(unique_id, model)
        self.stage = Stage.SUSCEPTIBLE
        self.astep = 0
        is_checkpoint = False
        params = [0, ageg, sexg, mort]
        self.agent_data = AgentDataClass(model, is_checkpoint, params)

       
    def alive(self):
        print(f'{self.unique_id} {self.agent_data.age_group} {self.agent_data.sex_group} is alive')

    def is_contagious(self):
        return (self.stage == Stage.EXPOSED) or (self.stage == Stage.ASYMPTOMATIC) or (self.stage == Stage.SYMPDETECTED)

    def dmult(self):
        # In this function, we simulate aerosol effects exhibited by droplets due to
        # both the contributions of a) a minimum distance with certainty of infection
        # and a the decreasing bioavailability of droplets, modeled as a sigmoid function.
        # Units are in meters. We assume that after 1.5 meter bioavailability decreases as a
        # sigmoid. This case supposses infrequent sneezing, but usual saliva droplets when
        # masks are not in use. A multiplier of k = 10 is used as a sharpening parameter
        # of the distribution and must be further callibrated.
        mult = 1.0

        if self.model.model_data.distancing >= 1.5:
            k = 10
            mult = 1.0 - (1.0 / (1.0 + np.exp(k*(-(self.model.model_data.distancing - 1.5) + 0.5))))

        return mult

    # In this function, we count effective interactants
    def interactants(self):
        count = 0

        if (self.stage != Stage.DECEASED) and (self.stage != Stage.RECOVERED):
            for agent in self.model.grid.get_cell_list_contents([self.pos]):
                if agent.unique_id != self.unique_id:
                    if not(agent.agent_data.isolated) or self.agent_data.isolated_but_inefficient:
                        count = count + 1

        return count

    # A function that applies a contact tracing test
    def test_contact_trace(self):
        # We may have an already tested but it had a posterior contact and became infected
        if self.stage == Stage.SUSCEPTIBLE:
            self.agent_data.tested_traced = True
        elif self.stage == Stage.EXPOSED:
            self.agent_data.tested_traced = True

            if bernoulli_rvs(self.model.model_data.prob_asymptomatic):
                    self.stage = Stage.ASYMPDETECTED
            else:
                self.stage = Stage.SYMPDETECTED
        elif self.stage == Stage.ASYMPTOMATIC:
            self.stage = Stage.ASYMPDETECTED
            self.agent_data.tested_traced = True
        else:
            return

    def add_contact_trace(self, other):
        if self.model.model_data.tracing_now:
            self.agent_data.contacts.add(other)

    #helper function that reveals if an agent is vaccinated
    def is_vaccinated(self):
        return self.agent_data.vaccinated


    #Vaccination decision process, prone to change to find the ideal method.
    #Implementing the standard set that those who are older will be prioritized.
    #For now implementing random vaccination.

    def general_vaccination_chance(self):
        eligible_count = compute_age_group_count(self.model, self.agent_data.age_group)
        vaccination_chance = 1/eligible_count
        if self.stage == Stage.ASYMPTOMATIC or self.stage == Stage.SUSCEPTIBLE or self.stage == Stage.EXPOSED:
            if bernoulli_rvs(vaccination_chance):
                return True
            return False
        return False

    def should_be_vaccinated(self):
        if self.general_vaccination_chance():
            if self.agent_data.age_group == AgeGroup.C80toXX and self.model.model_data.vaccination_stage == VaccinationStage.C80toXX:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C70to79 and self.model.model_data.vaccination_stage == VaccinationStage.C70to79:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C60to69 and self.model.model_data.vaccination_stage == VaccinationStage.C60to69:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C50to59 and self.model.model_data.vaccination_stage == VaccinationStage.C50to59:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C40to49 and self.model.model_data.vaccination_stage == VaccinationStage.C40to49:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C30to39 and self.model.model_data.vaccination_stage == VaccinationStage.C30to39:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C20to29 and self.model.model_data.vaccination_stage == VaccinationStage.C20to29:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C10to19 and self.model.model_data.vaccination_stage == VaccinationStage.C10to19:
                update_vaccination_stage(self.model)
                return True
            elif self.agent_data.age_group == AgeGroup.C00to09 and self.model.model_data.vaccination_stage == VaccinationStage.C00to09:
                update_vaccination_stage(self.model)
                return True
            else :
                update_vaccination_stage(self.model)
                return False
        return False

    def step(self):
        # We compute unemployment in general as a probability of 0.00018 per day.
        # In 60 days, this is equivalent to a probability of 1% unemployment filings.
        if self.agent_data.employed:
            if self.agent_data.isolated:
                if bernoulli_rvs(32*0.00018/self.model.model_data.dwell_15_day):
                    self.agent_data.employed = False
            else:
                if bernoulli_rvs(8*0.00018/self.model.model_data.dwell_15_day):
                    self.agent_data.employed = False

        # We also compute the probability of re-employment, which is at least ten times
        # as smaller in a crisis.
        if not(self.agent_data.employed):
            if bernoulli_rvs(0.000018/self.model.model_data.dwell_15_day):
                self.agent_data.employed = True


       # Social distancing
        if not(self.agent_data.in_distancing) and (self.astep >= self.model.model_data.distancing_start):
            self.agent_data.prob_contagion = self.dmult() * self.model.model_data.prob_contagion_base
            self.agent_data.in_distancing = True

        if self.agent_data.in_distancing and (self.astep >= self.model.model_data.distancing_end):
            self.agent_data.prob_contagion = self.model.model_data.prob_contagion_base
            self.agent_data.in_distancing = False

        # Testing
        if not(self.agent_data.in_testing) and (self.astep >= self.model.model_data.testing_start):
            self.agent_data.test_chance = self.model.model_data.testing_rate
            self.agent_data.in_testing = True

        if self.agent_data.in_testing and (self.astep >= self.model.model_data.testing_end):
            self.agent_data.test_chance = 0
            self.agent_data.in_testing = False


        #Implementing the vaccine
        #Will process based on whether all older agents in an older group are vaccinated
        if (not(self.agent_data.vaccinated) or self.agent_data.dosage_eligible) and self.model.model_data.vaccination_now and (not(self.agent_data.fully_vaccinated) and (self.agent_data.vaccine_count < self.model.model_data.vaccine_dosage)):
            if self.should_be_vaccinated() and self.model.model_data.vaccine_count > 0 and self.agent_data.vaccine_willingness:
                if not (bernoulli_rvs(0.1)):  # Chance that someone doesnt show up for the vaccine/ vaccine expires.
                    self.agent_data.vaccinated = True
                    self.agent_data.vaccination_day = self.model.stepno
                    self.agent_data.vaccine_count = self.agent_data.vaccine_count + 1
                    self.agent_data.dosage_eligible = False
                    self.model.model_data.vaccine_count = self.model.model_data.vaccine_count - 1
                    self.model.model_data.vaccinated_count = self.model.model.data.vaccinated_count + 1

                else:
                    other_agent = self.random.choice(self.model.schedule.agents)
                    while not(other_agent.dosage_eligible and other_agent.vaccine_willingness):
                        other_agent = self.random.choice(self.model.schedule.agents)
                    other_agent.vaccinated = True
                    other_agent.vaccination_day = self.model.stepno
                    other_agent.vaccine_count = other_agent.vaccine_count +1
                    other_agent.dosage_eligible = False
                    self.model.model_data.vaccinated_count = self.model.model_data.vaccinated_count + 1
                    self.model.model_data.vaccine_count = self.model.model_data.vaccine_count - 1


        # Self isolation is tricker. We only isolate susceptibles, incubating and asymptomatics
        if not(self.agent_data.in_isolation):
            if (self.astep >= self.model.model_data.isolation_start):
                if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.EXPOSED) or \
                    (self.stage == Stage.ASYMPTOMATIC):
                    if bool(bernoulli_rvs(self.model.model_data.isolation_rate)):
                        self.agent_data.isolated = True
                    else:
                        self.agent_data.isolated = False
                    self.agent_data.in_isolation = True
            elif (self.astep >= self.model.model_data.isolation_end):
                if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.EXPOSED) or \
                    (self.stage == Stage.ASYMPTOMATIC):
                    if bool(bernoulli_rvs(self.model.model_data.after_isolation)):
                        self.agent_data.isolated = True
                    else:
                        self.agent_data.isolated = False
                    self.agent_data.in_isolation = True

                    
        # Using a similar logic, we remove isolation for all relevant agents still locked
        if self.agent_data.in_isolation and (self.astep >= self.model.model_data.isolation_end):
            if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.EXPOSED) or \
                (self.stage == Stage.ASYMPTOMATIC):
                self.agent_data.isolated = False
                self.agent_data.in_isolation = False


        #Implementing the current safety factor for maximum effectiveness

        vaccination_time = self.model.stepno - self.agent_data.vaccination_day
        #In this model I will assume that the vaccine is only half as effective once 2 weeks have passed given one dose.
        effective_date = self.model.model_data.dwell_15_day * 14
        if (vaccination_time < effective_date) and self.agent_data.vaccinated == True:
            self.agent_data.safetymultiplier = 1 - (self.model.agent_data.effectiveness_per_dosage * (vaccination_time/effective_date)) - self.agent_data.current_effectiveness #Error the vaccination will go to 0 once it is done.
        else:
            self.agent_data.current_effectiveness = self.model.model_data.effectiveness_per_dosage * self.agent_data.vaccine_count
            self.agent_data.safetymultiplier = 1 - self.agent_data.current_effectiveness * self.model.model_data.variant_data_list[self.agent_data.variant]["Vaccine_Multiplier"]
            if (self.agent_data.vaccine_count < self.model.model_data.vaccine_dosage):
                self.agent_data.dosage_eligible = True  # Once this number is false, the person is eligible and is not fully vaccinated.
            elif self.agent_data.fully_vaccinated == False:
                self.agent_data.dosage_eligible = False
                self.agent_data.fully_vaccinated = True
                self.model.model_data.fully_vaccinated_count = self.model.model_data.fully_vaccinated_count + 1


        # Using the model, determine if a susceptible individual becomes infected due to
        # being elsewhere and returning to the community
        if self.stage == Stage.SUSCEPTIBLE:
            #             if bernoulli_rvs(self.model.rate_inbound):
            #                 self.stage = Stage.EXPOSED
            #                 self.model.generally_infected = self.model.generally_infected + 1
            #
            #         if self.stage == Stage.SUSCEPTIBLE:
            #             # Important: infected people drive the spread, not
            #             # the number of healthy ones
            #
            #             # If testing is available and the date is reached, test
            #             # Testing of a healthy person should maintain them as
            # still susceptible.
            # We take care of testing probability at the top level step
            # routine to avoid this repeated computation
            if not(self.agent_data.tested or self.agent_data.tested_traced) and bernoulli_rvs(self.agent_data.test_chance):
                self.agent_data.tested = True
                self.model.model_data.cumul_test_cost = self.model.model_data.cumul_test_cost + self.model.model_data.test_cost
            # First opportunity to get infected: contact with others
            # in near proximity
            cellmates = self.model.grid[self.pos[0]][self.pos[1]]
            infected_contact = 0 #Changed to account for asymptomatic threat of infection

            # Isolated people should only be contagious if they do not follow proper
            # shelter-at-home measures

            #Future implementaions would allow for multiple strains of the virus to stack on top of the same agent if exposed more than once but there is not much research showing what would really happen or what
            #values we would have to account for
            variant = "Standard"
            for c in cellmates:
                    if c.is_contagious() and (c.stage == Stage.SYMPDETECTED or c.stage == Stage.SEVERE) and self.agent_data.variant_immune[c.agent_data.variant] == False:
                        c.add_contact_trace(self)
                        if self.agent_data.isolated and bernoulli_rvs(1 - self.model.model_data.prob_isolation_effective):
                            self.agent_data.isolated_but_inefficient = True
                            infected_contact = 1
                            variant = c.agent_data.variant
                            break
                        else:
                            infected_contact = 1
                            variant = c.agent_data.variant
                            break
                    elif c.is_contagious() and (c.stage == Stage.ASYMPTOMATIC or c.stage == Stage.ASYMPDETECTED) and self.agent_data.variant_immune[c.agent_data.variant] == False:
                        c.add_contact_trace(self)
                        if self.agent_data.isolated and bernoulli_rvs(1 - self.model.model_data.prob_isolation_effective):
                            self.agent_data.isolated_but_inefficient = True
                            infected_contact = 2
                            variant = c.agent_data.variant
                        else:
                            infected_contact = 2
                            variant = c.agent_data.variant

            # Value is computed before infected stage happens
            isolation_private_divider = 1
            isolation_public_divider = 1


            if self.agent_data.employed:
                if self.agent_data.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01


                self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                    ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.SUSCEPTIBLE])*isolation_private_divider
                self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                    ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.SUSCEPTIBLE])*isolation_public_divider
            else:
                self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + 0
                self.agent_data.cumul_public_value = self.agent_data.cumul_public_value - 2*self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.SUSCEPTIBLE]


            current_prob = self.agent_data.prob_contagion * self.model.model_data.variant_data_list[variant]["Contagtion_Multiplier"]
            if self.agent_data.vaccinated:
                current_prob = current_prob * self.agent_data.safetymultiplier

            if infected_contact == 2:
                current_prob = current_prob * 0.42

            if infected_contact > 0:
                if self.agent_data.isolated:
                    if bernoulli_rvs(current_prob) and not(bernoulli_rvs(self.model.model_data.prob_isolation_effective)):
                        self.stage = Stage.EXPOSED
                        self.agent_data.variant = variant
                        self.model.model_data.generally_infected = self.model.model_data.generally_infected + 1
                else:
                    if bernoulli_rvs(current_prob):
                        #Added vaccination account after being exposed to determine exposure.
                        self.stage = Stage.EXPOSED
                        self.agent_data.variant = variant
                        self.model.model_data.generally_infected = self.model.model_data.generally_infected + 1


            # Second opportunity to get infected: residual droplets in places
            # TODO

            if not(self.agent_data.isolated):
                self.move()
        elif self.stage == Stage.EXPOSED:
            # Susceptible patients only move and spread the disease.
            # If the incubation time is reached, it is immediately 
            # considered as detected since it is severe enough.

            # We compute the private value as usual
            cellmates = self.model.grid.get_cell_list_contents([self.pos])

            isolation_private_divider = 1
            isolation_public_divider = 1

            if self.agent_data.employed:
                if self.agent_data.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01
                
                self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                    ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.EXPOSED])*isolation_private_divider
                self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                    ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.EXPOSED])*isolation_public_divider
            else:
                self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + 0
                self.agent_data.cumul_public_value = self.agent_data.cumul_public_value - 2*self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.EXPOSED]

            # Assignment is less expensive than comparison
            do_move = True

            current_prob_asymptomatic = self.model.model_data.prob_asymptomatic * self.model.model_data.variant_data_list[self.agent_data.variant]["Asymtpomatic_Multiplier"]
            if self.agent_data.vaccinated:
                current_prob_asymptomatic = 1-(1-self.model.model_data.prob_asymptomatic) * self.agent_data.safetymultiplier #Probability of asymptomatic becomes 1-(probability of symptomatic)*safety_multiplier


            # If testing is available and the date is reached, test
            if not(self.agent_data.tested or self.agent_data.tested_traced) and bernoulli_rvs(self.agent_data.test_chance):
                if bernoulli_rvs(current_prob_asymptomatic):
                    self.stage = Stage.ASYMPDETECTED
                else:
                    self.stage = Stage.SYMPDETECTED
                    do_move = False
                
                self.agent_data.tested = True
                self.model.model_data.cumul_test_cost = self.model.model_data.cumul_test_cost + self.model.model_data.test_cost
            else:
                if self.agent_data.curr_incubation < self.agent_data.incubation_time:
                    self.agent_data.curr_incubation = self.agent_data.curr_incubation + 1
                else:
                    if bernoulli_rvs(current_prob_asymptomatic):
                        self.stage = Stage.ASYMPTOMATIC
                    else:
                        self.stage = Stage.SYMPDETECTED
                        do_move = False

            # Now, attempt to move
            if do_move and not(self.agent_data.isolated):
                self.move()
            
            # Perform the move once the condition has been determined
        elif self.stage == Stage.ASYMPTOMATIC:
            # Asymptomayic patients only roam around, spreading the
            # disease, ASYMPDETECTEDimmune system
            cellmates = self.model.grid.get_cell_list_contents([self.pos])

            isolation_private_divider = 1
            isolation_public_divider = 1

            if self.agent_data.employed:
                if self.agent_data.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01
                
                    self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                        ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.ASYMPTOMATIC])*isolation_private_divider
                    self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                        ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPTOMATIC])*isolation_public_divider
                else:
                    self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + 0
                    self.agent_data.cumul_public_value = self.agent_data.cumul_public_value - 2*self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPTOMATIC]

            if not(self.agent_data.tested or self.agent_data.tested_traced) and bernoulli_rvs(self.agent_data.test_chance):
                self.stage = Stage.ASYMPDETECTED
                self.agent_data.tested = True
                self.model.model_data.cumul_test_cost = self.model.model_data.cumul_test_cost + self.model.model_data.test_cost

            if self.agent_data.curr_recovery >= self.agent_data.recovery_time:
                self.stage = Stage.RECOVERED
                self.agent_data.variant_immune[self.agent_data.variant] = True
            else:
                self.agent_data.curr_recovery  += 1

            if not (self.agent_data.isolated):
                self.move()

                    
        elif self.stage == Stage.SYMPDETECTED:
            # Once a symptomatic patient has been detected, it does not move and starts
            # the road to severity, recovery or death. We assume that, by reaching a health
            # unit, they are tested as positive.
            self.agent_data.isolated = True
            self.agent_data.tested = True

            current_severe_chance = self.agent_data.mortality_value * self.model.model_data.variant_data_list[self.agent_data.variant]["Mortality_Multiplier"] * (1/(self.model.model_data.dwell_15_day))
            if (self.agent_data.vaccinated):
                current_severe_chance = current_severe_chance * self.agent_data.safetymultiplier


            # Contact tracing logic: use a negative number to indicate trace exhaustion
            if self.model.model_data.tracing_now and self.agent_data.tracing_counter >= 0:
                # Test only when the count down has been reached
                if self.agent_data.tracing_counter == self.agent_data.tracing_delay:
                    for t in self.agent_data.contacts:
                        t.test_contact_trace()

                    self.agent_data.tracing_counter = -1
                else:
                    self.agent_data.tracing_counter = self.agent_data.tracing_counter + 1
            
            self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.SYMPDETECTED]
            self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.SYMPDETECTED]

            if self.agent_data.curr_incubation + self.agent_data.curr_recovery < self.agent_data.incubation_time + self.agent_data.recovery_time:
                self.agent_data.curr_recovery = self.agent_data.curr_recovery + 1

                if bernoulli_rvs(current_severe_chance):
                    self.stage = Stage.SEVERE
            else:
                self.stage = Stage.RECOVERED
                self.agent_data.variant_immune[self.agent_data.variant] = True
        elif self.stage == Stage.ASYMPDETECTED:
            self.agent_data.isolated = True

            # Contact tracing logic: use a negative number to indicate trace exhaustion
            if self.model.model_data.tracing_now and self.agent_data.tracing_counter >= 0:
                # Test only when the count down has been reached
                if self.agent_data.tracing_counter == self.agent_data.tracing_delay:
                    for t in self.agent_data.contacts:
                        t.test_contact_trace()

                    self.agent_data.tracing_counter = -1
                else:
                    self.agent_data.tracing_counter = self.agent_data.tracing_counter + 1

            self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.ASYMPDETECTED]
            self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPDETECTED]

            # The road of an asymptomatic patients is similar without the prospect of death
            if self.agent_data.curr_incubation + self.agent_data.curr_recovery < self.agent_data.incubation_time + self.agent_data.recovery_time:
               self.agent_data.curr_recovery = self.agent_data.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
                self.agent_data.variant_immune[self.agent_data.variant] = True

        elif self.stage == Stage.SEVERE:            
            self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.SEVERE]
            self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.SEVERE]

            # Severe patients are in ICU facilities
            if self.agent_data.curr_recovery < self.agent_data.recovery_time:
                # Not recovered yet, may pass away depending on prob.
                if self.model.model_data.bed_count > 0 and self.agent_data.occupying_bed == False:
                    self.agent_data.occupying_bed = True
                    self.model.model_data.bed_count -= 1
                if self.agent_data.occupying_bed == False:
                    if bernoulli(1/(self.agent_data.recovery_time)): #Chance that someone dies at this stage is current_time/time that they should recover. This ensures that they may die at a point during recovery.
                        self.stage = Stage.DECEASED
                # else:
                #     if bernoulli(0 * 1/self.recovery_time): #Chance that someone dies on the bed is 42% less likely so I will also add that they have a 1/recovery_time chance of dying
                #         self.stage = Stage.DECEASED
                #         self.occupying_bed == False
                #         self.model.bed_count += 1
                self.agent_data.curr_recovery = self.agent_data.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
                self.agent_data.variant_immune[self.variant] = True
                if (self.agent_data.occupying_bed == True):
                    self.agent_data.occupying_bed == False
                    self.model.model_data.bed_count += 1



        elif self.stage == Stage.RECOVERED:
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            
            if self.agent_data.employed:
                isolation_private_divider = 1
                isolation_public_divider = 1

                if self.agent_data.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01

                self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                    ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.RECOVERED])*isolation_private_divider
                self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                    ((len(cellmates) - 1) * self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.RECOVERED])*isolation_public_divider
            else:
                self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + 0
                self.agent_data.cumul_public_value = self.agent_data.cumul_public_value - 2*self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.RECOVERED]


            # A recovered agent can now move freely within the grid again
            self.agent_data.curr_recovery = 0
            self.agent_data.isolated = False
            self.agent_data.isolated_but_inefficient = False

            infected_contact = 0
            variant = "Standard"
            for c in cellmates:
                if c.is_contagious() and self.model.model_data.variant_data_list[c.variant]["Reinfection"] == True and (c.stage == Stage.SYMPDETECTED or c.stage == Stage.SEVERE) and self.agent_data.variant_immune[c.variant] != True:
                    if self.agent_data.isolated and bernoulli_rvs(1 - self.model.model_data.prob_isolation_effective):
                        self.agent_data.isolated_but_inefficient = True
                        infected_contact = 1
                        variant = c.variant
                        break
                    else:
                        infected_contact = 1
                        variant = c.variant
                        break
                elif c.is_contagious() and (c.stage == Stage.ASYMPTOMATIC or c.stage == Stage.ASYMPDETECTED) and self.agent_data.variant_immune[c.variant] == False:
                    c.add_contact_trace(self)
                    if self.agent_data.isolated and bernoulli_rvs(1 - self.model.model_data.prob_isolation_effective):
                        self.agent_data.isolated_but_inefficient = True
                        infected_contact = 2
                        variant = c.variant
                    else:
                        infected_contact = 2
                        variant = c.variant

            current_prob = self.agent_data.prob_contagion * self.model.model_data.variant_data_list[variant]["Contagtion_Multiplier"]
            if self.agent_data.vaccinated:
                current_prob = current_prob * self.agent_data.safetymultiplier

            if infected_contact == 2:
                current_prob = current_prob * 0.42

            if infected_contact > 0:
                if self.agent_data.isolated:
                    if bernoulli_rvs(current_prob) and not (bernoulli_rvs(self.model.model_data.prob_isolation_effective)):
                        self.stage = Stage.EXPOSED
                        self.agent_data.variant = variant
                else:
                    if bernoulli_rvs(current_prob):
                        # Added vaccination account after being exposed to determine exposure.
                        self.stage = Stage.EXPOSED
                        self.agent_data.variant = variant


            self.move()
        elif self.stage == Stage.DECEASED:
            self.agent_data.cumul_private_value = self.agent_data.cumul_private_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PRIVATE][Stage.DECEASED]
            self.agent_data.cumul_public_value = self.agent_data.cumul_public_value + \
                self.model.model_data.stage_value_dist[ValueGroup.PUBLIC][Stage.DECEASED]
        else:
            # If we are here, there is a problem 
            sys.exit("Unknown stage: aborting.")


        #Insert a new trace into the database (AgentDataClass)
        id = str(uuid.uuid4())
        agent_params = [(
            id, 
            self.agent_data.age_group.value,
            self.agent_data.sex_group.value, 
            self.agent_data.vaccine_willingness, 
            self.agent_data.incubation_time, 
            self.agent_data.dwelling_time, 
            self.agent_data.recovery_time, 
            self.agent_data.prob_contagion, 
            self.agent_data.mortality_value, 
            self.agent_data.severity_value,
            self.agent_data.curr_dwelling,
            self.agent_data.curr_incubation,
            self.agent_data.curr_recovery,
            self.agent_data.curr_asymptomatic,
            self.agent_data.isolated,
            self.agent_data.isolated_but_inefficient,
            self.agent_data.test_chance,
            self.agent_data.in_isolation,
            self.agent_data.in_distancing,
            self.agent_data.in_testing,
            self.agent_data.astep,
            self.agent_data.tested,
            self.agent_data.occupying_bed,
            self.agent_data.cumul_private_value,
            self.agent_data.cumul_public_value,
            self.agent_data.employed,
            self.agent_data.tested_traced,
            self.agent_data.tracing_delay,
            self.agent_data.tracing_counter,
            self.agent_data.vaccinated,
            self.agent_data.safetymultiplier,
            self.agent_data.current_effectiveness,
            self.agent_data.vaccination_day,
            self.agent_data.vaccine_count,
            self.agent_data.dosage_eligible,
            self.agent_data.fully_vaccinated,
            self.agent_data.variant
        )]

        self.model.db.insert_agent(agent_params)
        self.model.db.commit()

        self.astep = self.astep + 1

    def move(self):
        # If dwelling has not been exhausted, do not move
        if self.agent_data.curr_dwelling > 0:
            self.agent_data.curr_dwelling = self.agent_data.curr_dwelling - 1

        # If dwelling has been exhausted, move and replenish the dwell
        else:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            new_position = self.random.choice(possible_steps)

            self.model.grid.move_agent(self, new_position)
            self.agent_data.curr_dwelling = poisson_rvs(self.model.model_data.avg_dwell)


########################################

def compute_variant_stage(model, variant, stage):
    count = 0
    for agent in model.schedule.agents:
        if stage == Stage.SUSCEPTIBLE:
            if agent.agent_data.variant == variant:
                count += 1
        else:
            if agent.stage == stage and agent.agent_data.variant == variant:
                count += 1
    return count

def compute_vaccinated_stage(model, stage):
    count = 0
    for agent in model.schedule.agents:
        if agent.stage == stage and agent.agent_data.vaccinated == True:
            count += count
    vaccinated_count = compute_vaccinated_count(model)
    if vaccinated_count == 0:
        return 0
    else:
        return count

def compute_stage(model,stage):
    return count_type(model,stage)

def count_type(model, stage):
    count = 0
    for agent in model.schedule.agents:
        if agent.stage == stage:
            count = count + 1

    return count

def compute_isolated(model):
    count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.isolated:
            count = count + 1
    return count

def compute_employed(model):
    count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.employed:
            count = count + 1

    return count

def compute_unemployed(model):
    count = 0

    for agent in model.schedule.agents:
        if not(agent.agent_data.employed):
            count = count + 1

    return count

def compute_contacts(model):
    count = 0
    for agent in model.schedule.agents:
        count = count + agent.interactants()
    return count

def compute_stepno(model):
    return model.stepno

def compute_cumul_private_value(model):
    value = 0
    for agent in model.schedule.agents:
        value = value + agent.agent_data.cumul_private_value
    return np.sign(value)*np.power(np.abs(value), model.model_data.alpha_private)/model.num_agents

def compute_cumul_public_value(model):
    value = 0

    for agent in model.schedule.agents:
        value = value + agent.agent_data.cumul_public_value

    return np.sign(value)*np.power(np.abs(value), model.model_data.alpha_public)/model.num_agents


#  Changed the method for calculating the test cost. This will occur in more linear time,
#  can also differentiate being tested from being percieved as infected. This will be a rising value,
#  will change testing to be based on necessity along with the vaccine.

def compute_cumul_testing_cost(model):
    return model.model_data.cumul_test_cost

def compute_cumul_vaccination_cost(model):
    return model.model_data.cumul_vaccine_cost

def compute_total_cost(model):
    return model.model_data.cumul_test_cost + model.model_data.cumul_vaccine_cost

def compute_tested(model):
    tested = 0

    for agent in model.schedule.agents:
        if agent.agent_data.tested:
            tested = tested + 1

    return tested

# Added to track the number of vaccinated agents.
def compute_vaccinated(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.vaccinated:
            vaccinated_count = vaccinated_count + 1

    return vaccinated_count


def compute_vaccinated_count(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.vaccinated:
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count

def compute_vaccinated_1(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.vaccine_count == 1:
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count

def compute_vaccinated_2(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.vaccine_count == 2:
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count

def compute_willing_agents(model):
    count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.vaccine_willingness:
            count = count + 1
    return count


# Another helper function to determine the vaccination of agents based on agegroup.
def compute_vaccinated_in_group_count(model,agegroup):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.agent_data.vaccinated) and (agent.agent_data.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count



def compute_vaccinated_in_group(model,agegroup):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.agent_data.vaccinated) and (agent.agent_data.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count


def compute_fully_vaccinated_in_group(model,agegroup):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.agent_data.fully_vaccinated) and (agent.agent_data.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count


def compute_vaccinated_in_group_percent_vaccine_count(model, agegroup, count):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.agent_data.vaccine_count == count) and (agent.agent_data.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count


def cumul_effectiveness_per_group_vaccinated(model,agegroup):
    vaccinated_count = 0
    effectiveness = 0
    for agent in model.schedule.agents:
        if (agent.agent_data.age_group == agegroup and agent.agent_data.vaccinated == True):
            vaccinated_count = vaccinated_count + 1
            effectiveness += agent.agent_data.safetymultiplier
    if (vaccinated_count > 0):
        return 1-(effectiveness / vaccinated_count)
    else:
        return 0

def cumul_effectiveness_per_group(model,agegroup):
    agent_count = 0
    effectiveness = 0
    for agent in model.schedule.agents:
        if (agent.agent_data.age_group == agegroup):
            agent_count = agent_count + 1
            effectiveness += agent.agent_data.safetymultiplier
    if (agent_count > 0):
        return 1-(effectiveness / agent_count)
    else:
        return 0

def compute_age_group_count(model,agegroup):
    count = 0
    for agent in model.schedule.agents:
        if agent.agent_data.age_group == agegroup:
            count = count + 1
    return count

def compute_eligible_age_group_count(model,agegroup):
    count = 0
    for agent in model.schedule.agents:
        if (agent.agent_data.age_group == agegroup) and (agent.agent_data.stage == Stage.SUSCEPTIBLE or agent.agent_data.stage == Stage.EXPOSED or agent.agent_data.stage == Stage.ASYMPTOMATIC) and agent.agent_data.dosage_eligible and agent.agent_data.vaccine_willingness:
            count = count + 1
    return count


def update_vaccination_stage(model):
    initial_stage = model.model_data.vaccination_stage
    # if compute_eligible_age_group_count(model, AgeGroup.C80toXX) < 1:
    #     model.model_data.vaccination_stage = VaccinationStage.C70to79
    #     if compute_eligible_age_group_count(model, AgeGroup.C70to79) < 1:
    #         model.model_data.vaccination_stage = VaccinationStage.C60to69
    #         if compute_eligible_age_group_count(model, AgeGroup.C60to69) < 1:
    #             model.model_data.vaccination_stage = VaccinationStage.C50to59
    #             if compute_eligible_age_group_count(model, AgeGroup.C50to59) < 1:
    #                 model.model_data.vaccination_stage = VaccinationStage.C40to49
    #                 if compute_eligible_age_group_count(model, AgeGroup.C40to49) < 1:
    #                     model.model_data.vaccination_stage = VaccinationStage.C30to39
    #                     if compute_eligible_age_group_count(model, AgeGroup.C30to39) < 1:
    #                         model.model_data.vaccination_stage = VaccinationStage.C20to29
    #                         if compute_eligible_age_group_count(model, AgeGroup.C20to29) < 1:
    #                             model.model_data.vaccination_stage = VaccinationStage.C10to19
    #                             if compute_eligible_age_group_count(model, AgeGroup.C10to19) < 1:
    #                                 model.model_data.vaccination_stage = VaccinationStage.C00to09
    # else:
    #     model.model_data.vaccination_stage = VaccinationStage.C80toXX

    eligible_age_group_dict = {}
    eligible_age_group_dict[compute_eligible_age_group_count(model, AgeGroup.C80toXX)] = VaccinationStage.C70to79
    eligible_age_group_dict[compute_eligible_age_group_count(model, AgeGroup.C70to79)] = VaccinationStage.C60to69
    eligible_age_group_dict[compute_eligible_age_group_count(model, AgeGroup.C60to69)] = VaccinationStage.C50to59
    eligible_age_group_dict[compute_eligible_age_group_count(model, AgeGroup.C50to59)] = VaccinationStage.C40to49
    eligible_age_group_dict[compute_eligible_age_group_count(model, AgeGroup.C40to49)] = VaccinationStage.C30to39
    eligible_age_group_dict[compute_eligible_age_group_count(model, AgeGroup.C30to39)] = VaccinationStage.C20to29
    eligible_age_group_dict[compute_eligible_age_group_count(model, AgeGroup.C10to19)] = VaccinationStage.C00to09

    model.model_data.vaccination_stage = VaccinationStage.C80toXX
    for key,value in sorted(eligible_age_group_dict.items(), reverse=True):
        if (key < 1):
            model.model_data.vaccination_stage = value

    if initial_stage != model.model_data.vaccination_stage:
        print(f"Vaccination stage is now {model.model_data.vaccination_stage}")


def compute_willing_group_count(model, agegroup):
    count = 0
    for agent in model.schedule.agents:
        if(agent.agent_data.vaccine_willingness):
            count += 1
    return count

def compute_traced(model):
    tested = 0

    for agent in model.schedule.agents:
        if agent.agent_data.tested_traced:
            tested = tested + 1

    return tested


def compute_total_processor_usage(model):
    if model.stepno % model.model_data.dwell_15_day == 0:
        processes = psu.cpu_percent(1, True)
        process_count = 0
        for idx, process in enumerate(processes):
            if (process > 0.0):
                process_count = process_count + 1
        return process_count
    else:
        return 0

def compute_processor_usage(model, processoridx):
    if model.stepno % model.model_data.dwell_15_day == 0:
        processes = psu.cpu_percent(1, True)
        for idx, process in enumerate(processes):
            if (idx == processoridx):
                return process
        return "Out of range"
    else:
        return 0

def compute_eff_reprod_number(model):
    prob_contagion = 0.0
    
    # Adding logic to better compute R(t)
    exposed = 0.0
    asymptomatics = 0.0
    symptomatics = 0.0
    
    exp_time = 0.0
    asympt_time = 0.0
    sympt_time = 0.0

    for agent in model.schedule.agents:
        if agent.stage == Stage.EXPOSED:
            exposed = exposed + 1
            exp_time = exp_time + agent.agent_data.incubation_time
            prob_contagion = agent.agent_data.prob_contagion
        elif agent.stage == Stage.SYMPDETECTED:
            # NOTE: this part needs to be adapted to model hospital transmission in further detail
            symptomatics = symptomatics + 1
            sympt_time = sympt_time + agent.agent_data.incubation_time
            prob_contagion = agent.agent_data.prob_contagion
        elif agent.stage == Stage.ASYMPTOMATIC:
            asymptomatics = asymptomatics + 1
            asympt_time = asympt_time + agent.agent_data.incubation_time + agent.agent_data.recovery_time
            prob_contagion = agent.agent_data.prob_contagion
        else:
            continue

    total = exposed + symptomatics + asymptomatics

    # Compute partial contributions
    times = []

    if exposed != 0:
        times.append(exp_time/exposed)

    if symptomatics != 0:
        times.append(sympt_time/symptomatics)

    if asymptomatics != 0 and symptomatics != 0:
        times.append(asympt_time/symptomatics)

    if total != 0:
        infectious_period = np.mean(times)
    else:
        infectious_period = 0

    avg_contacts = compute_contacts(model)
    return model.model_data.kmob * model.model_data.repscaling * prob_contagion * avg_contacts * infectious_period

def compute_num_agents(model):
    return model.num_agents

def compute_vaccine_count(model):
    return model.model_data.vaccine_count

def compute_datacollection_time(model):
    return model.datacollection_time

def compute_step_time(model):
    return model.step_time

def compute_generally_infected(model):
    return model.model_data.generally_infected

def compute_fully_vaccinated_count(model):
    return model.model_data.fully_vaccinated_count




class CovidModel(Model):
    """ A model to describe parameters relevant to COVID-19"""
    def __init__(self, num_agents, width, height, kmob, repscaling, rate_inbound, age_mortality,
                 sex_mortality, age_distribution, sex_distribution, prop_initial_infected,
                 proportion_asymptomatic, proportion_severe, avg_incubation_time, avg_recovery_time, prob_contagion,
                 proportion_isolated, day_start_isolation, days_isolation_lasts, after_isolation, prob_isolation_effective, social_distance,
                 day_distancing_start, days_distancing_lasts, proportion_detected, day_testing_start, days_testing_lasts, 
                 new_agent_proportion, new_agent_start, new_agent_lasts, new_agent_age_mean, new_agent_prop_infected,
                 day_tracing_start, days_tracing_lasts, stage_value_matrix, test_cost, alpha_private, alpha_public, proportion_beds_pop, day_vaccination_begin,
                 day_vaccination_end, effective_period, effectiveness, distribution_rate, cost_per_vaccine, vaccination_percent, variant_data, 
                 # policy_data,
                 db, dummy=0):

        print("Made it to the model")
        self.running = True
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.stepno = 0
        self.datacollection_time = 0
        self.step_time = 0
        self.db = db
        
        dwell_15_day = 96
        vaccine_dosage = 2
        repscaling = 1
        testing_start = day_testing_start* dwell_15_day
        tracing_start = day_tracing_start* dwell_15_day
        isolation_start = day_start_isolation*dwell_15_day
        distancing_start = day_distancing_start*dwell_15_day
        new_agent_start=new_agent_start*dwell_15_day
        max_bed_available = num_agents * proportion_beds_pop

        self.model_data = ModelDataClass (
            age_mortality=age_mortality, 
            sex_mortality=sex_mortality, 
            age_distribution=age_distribution, 
            sex_distribution=sex_distribution,
            stage_value_dist=stage_value_matrix,
            test_cost=test_cost, 
            alpha_private=alpha_private, 
            alpha_public=alpha_public,
            fully_vaccinated_count=0, 
            prop_initial_infected=prop_initial_infected, 
            generally_infected=0, 
            cumul_vaccine_cost=0,
            cumul_test_cost=0, 
            total_costs=0, 
            variant_data_list={},
            agent_parameter_names=[],
            dwell_15_day=dwell_15_day,
            avg_dwell=4,
            avg_incubation=int(round(avg_incubation_time * dwell_15_day)),
            repscaling=repscaling,
            prob_contagion_base=prob_contagion / repscaling,
            kmob=kmob,
            rate_inbound=rate_inbound/dwell_15_day,
            prob_contagion_places=0.001,
            prob_asymptomatic=proportion_asymptomatic,
            avg_recovery=avg_recovery_time * dwell_15_day,
            testing_rate=proportion_detected/(days_testing_lasts  * dwell_15_day),
            testing_start=testing_start,
            testing_end=testing_start + days_testing_lasts* dwell_15_day,
            tracing_start=tracing_start,
            tracing_end=tracing_start + days_tracing_lasts* dwell_15_day,
            tracing_now=False,
            isolation_rate=proportion_isolated,
            isolation_start=isolation_start,
            isolation_end=isolation_start + days_isolation_lasts*dwell_15_day,
            after_isolation=after_isolation,    # TODO: Remove this from the model dataclass, the scenario and the __init__ function.
            prob_isolation_effective=prob_isolation_effective,
            distancing=social_distance,
            distancing_start=distancing_start,
            distancing_end=distancing_start + days_distancing_lasts*dwell_15_day,
            new_agent_num=int(new_agent_proportion * self.num_agents),
            new_agent_start=new_agent_start,
            new_agent_end=new_agent_start + new_agent_lasts*dwell_15_day,
            new_agent_age_mean=new_agent_age_mean,
            new_agent_prop_infected=new_agent_prop_infected,
            vaccination_start=day_vaccination_begin * dwell_15_day, # TODO: check why we have two starting times
            vaccination_end=day_vaccination_end * dwell_15_day, # TODO: same here
            vaccination_now=False,  # TODO: change using the policy handler
            distribution_rate=distribution_rate, 
            vaccination_chance=distribution_rate/num_agents, # This is not actually a parameter, it is derived
            vaccination_stage=VaccinationStage.C80toXX, # Not a parameter
            vaccine_cost=cost_per_vaccine, # PH
            day_vaccination_begin=day_vaccination_begin, # TODO: see line 1196 above
            day_vaccination_end=day_vaccination_end, # TODO: see line 1197
            effective_period=effective_period, # PH
            effectiveness=effectiveness, # PH
            vaccine_count=0, 
            vaccinated_count=0,
            vaccinated_percent=vaccination_percent,
            vaccine_dosage=vaccine_dosage,
            effectiveness_per_dosage=effectiveness/vaccine_dosage,
            variant_start_times={},
            variant_start={},
            prob_severe=proportion_severe,
            max_bed_available = max_bed_available,
            bed_count=max_bed_available
        )

        self.pol_handler = PolicyHandler(dwell_15_day)

        #Read
        #pol_handler.parse_all_policies(policy_data)

        # Get default policies
        # pol_handler.set_defaults(self.model_data)

        print("model finished")
        # initial commit

        # insert a model into the database
        myid = str(uuid.uuid4())
        model_params = [(
            myid,
            self.model_data.test_cost,
            self.model_data.alpha_private,
            self.model_data.alpha_public,
            self.model_data.fully_vaccinated_count,
            self.model_data.prop_initial_infected,
            self.model_data.generally_infected,
            self.model_data.cumul_vaccine_cost,
            self.model_data.cumul_test_cost,
            self.model_data.total_costs,
            self.model_data.vaccination_chance, #
            self.model_data.vaccination_stage.value,
            self.model_data.vaccine_cost, #
            self.model_data.day_vaccination_begin, 
            self.model_data.day_vaccination_end,
            self.model_data.effective_period,
            self.model_data.effectiveness,
            self.model_data.distribution_rate,
            self.model_data.vaccine_count, #
            self.model_data.vaccinated_count, #
            self.model_data.vaccinated_percent, #
            self.model_data.vaccine_dosage,
            self.model_data.effectiveness_per_dosage,
            self.model_data.dwell_15_day,
            self.model_data.avg_dwell,
            self.model_data.avg_incubation,
            self.model_data.repscaling,
            self.model_data.prob_contagion_base,
            self.model_data.kmob,
            self.model_data.rate_inbound,
            self.model_data.prob_contagion_places,
            self.model_data.prob_asymptomatic,
            self.model_data.avg_recovery,
            self.model_data.testing_rate, #
            self.model_data.testing_start,
            self.model_data.testing_end,
            self.model_data.tracing_start,
            self.model_data.tracing_end,
            self.model_data.tracing_now,
            self.model_data.isolation_rate, #
            self.model_data.isolation_start,
            self.model_data.isolation_end,
            self.model_data.after_isolation,
            self.model_data.prob_isolation_effective, #
            self.model_data.distancing, #
            self.model_data.distancing_start,
            self.model_data.distancing_end,
            self.model_data.new_agent_num,
            self.model_data.new_agent_start,
            self.model_data.new_agent_end,
            self.model_data.new_agent_age_mean,
            self.model_data.new_agent_prop_infected,
            self.model_data.vaccination_start,
            self.model_data.vaccination_end,
            self.model_data.vaccination_now,
            self.model_data.prob_severe,
            self.model_data.max_bed_available,
            self.model_data.bed_count
        )]

        self.db.insert_model(model_params)
        self.db.commit()

        for variant in variant_data:
            self.model_data.variant_data_list[variant["Name"]] = {}
            self.model_data.variant_data_list[variant["Name"]]["Name"] = variant["Name"]
            self.model_data.variant_data_list[variant["Name"]]["Appearance"] = variant["Appearance"]
            self.model_data.variant_data_list[variant["Name"]]["Contagtion_Multiplier"] = variant["Contagtion_Multiplier"]
            self.model_data.variant_data_list[variant["Name"]]["Vaccine_Multiplier"] = variant["Vaccine_Multiplier"]
            self.model_data.variant_data_list[variant["Name"]]["Asymtpomatic_Multiplier"] = variant["Asymtpomatic_Multiplier"]
            self.model_data.variant_data_list[variant["Name"]]["Mortality_Multiplier"] = variant["Mortality_Multiplier"]
            self.model_data.variant_data_list[variant["Name"]]["Reinfection"] = variant["Reinfection"]

         # All parameter names of concern for agents. Must be kept in this form as a standard for loading into agent data. Add a new variable name before pos.
        #TODO (optional) make the production of the agent more rigourous instead of the brute force solution you have up there.
        self.agent_parameter_names = ['unique_id', 'stage', 'age_group', 'sex_group', 'vaccine_willingness',
                                      'incubation_time', 'dwelling_time', 'recovery_time', 'prob_contagion',
                                      'mortality_value', 'severity_value', 'curr_dwelling', 'curr_incubation',
                                      'curr_recovery', 'curr_asymptomatic', 'isolated', 'isolated_but_inefficient',
                                      'test_chance', 'in_isolation', 'in_distancing', 'in_testing', 'astep', 'tested',
                                      'occupying_bed', 'cumul_private_value', 'cumul_public_value', 'employed',
                                      'tested_traced', 'contacts', 'tracing_delay', 'tracing_counter', 'vaccinated',
                                      'safetymultiplier', 'current_effectiveness', 'vaccination_day', 'vaccine_count',
                                      'dosage_eligible', 'fully_vaccinated', 'variant', 'variant_immune', 'pos']

        self.model_reporters = {}
        # Closing of various businesses
        # TODO: at the moment, we assume that closing businesses decreases the dwell time.
        # A more proper implementation would a) use a power law distribution for dwell times
        # and b) assign a background of dwell times first, modifying them upwards later
        # for all cells.
        # Alternatively, shutting restaurants corresponds to 15% of interactions in an active day, and bars to a 7%
        # of those interactions
        self.variant_start_times = {}
        self.variant_start = {}

        # A dictionary to count the dwell time of an agent at a location; 
        # key is (agent, x, y) and value is count of dwell time
        self.dwell_time_at_locations = {}
        positions = [(x, y) for x, y in zip(range(self.grid.width), range(self.grid.height))]
        
        for i,j in positions:
            self.dwell_time_at_locations[(x, y)] = poisson_rvs(self.model.model_data.avg_dwell)

        for key in self.model_data.variant_data_list:
            self.variant_start_times[key] = self.model_data.variant_data_list[key]["Appearance"] * self.model_data.dwell_15_day
            self.variant_start[key] = False
            print(key)
            print(self.model_data.variant_data_list[key])
            print(self.model_data.variant_data_list[key]["Appearance"])


        # Now, a neat python trick: generate the spacing of entries and then build a map
        times_list = list(np.linspace(self.model_data.new_agent_start, self.model_data.new_agent_end, self.model_data.new_agent_num, dtype=int))
        self.new_agent_time_map = {x:times_list.count(x) for x in times_list}

        # We store a simulation specification in the database
        # Commit
        #print(self.model_data.vaccination_stage.value)

        # Create agents
        self.i = 0

        for ag in self.model_data.age_distribution:
            for sg in self.model_data.sex_distribution:
                r = self.model_data.age_distribution[ag]*self.model_data.sex_distribution[sg]
                num_agents = int(round(self.num_agents*r))
                mort = self.model_data.age_mortality[ag]*self.model_data.sex_mortality[sg]
                for k in range(num_agents):
                    a = CovidAgent(self.i, ag, sg, mort, self)
                    self.schedule.add(a)
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    self.grid.place_agent(a, (x,y))
                    self.i = self.i + 1

        processes = psu.cpu_percent(1, True)
        processes_dict = {}
        for idx, process in enumerate(processes):
            processor_name = "Processor " + str(idx)
            processes_dict[processor_name] = [compute_processor_usage, [self, idx]]
        processes_dict["Total_Processore_Use"] = compute_total_processor_usage


        age_vaccination_dict = {}

        for age in AgeGroup:
            age_group_name = "Vaccinated " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_vaccinated_in_group, [self, age]]
            age_group_name = "Cumulative_Effectiveness " + str(age.name)
            age_vaccination_dict[age_group_name] = [cumul_effectiveness_per_group, [self, age]]

        for age in AgeGroup:
            age_group_name = "Fully_Vaccinated " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_fully_vaccinated_in_group, [self, age]]

        for age in AgeGroup:
            age_group_name = "Vaccinated_1 " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_vaccinated_in_group_percent_vaccine_count, [self, age, 1]]

        for age in AgeGroup:
            age_group_name = "Vaccinated_2 " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_vaccinated_in_group_percent_vaccine_count, [self, age, 2]]

        variant_data_collection_dict = {}
        for variant in variant_data:
            for stage in Stage:
                variant_stage_name = str(variant["Name"]) + str(stage.name)
                if stage == Stage.SUSCEPTIBLE:
                    variant_stage_name = str(variant["Name"])+"_Total_Infected"
                print(variant_stage_name)
                variant_data_collection_dict[variant_stage_name] = [compute_variant_stage, [self, variant["Name"], stage]]

        vaccinated_status_dict = {}
        for stage in Stage:
            stage_name = "V " + str(stage.name)
            vaccinated_status_dict[stage_name] = [compute_vaccinated_stage, [self, stage]]

        agent_status_dict = {}
        for stage in Stage:
            stage_name = str(stage.name)
            agent_status_dict[stage_name] = [compute_stage, [self,stage]]


        # This is part of the summary
        prices_dict = { "CumulPrivValue": compute_cumul_private_value,
            "CumulPublValue": compute_cumul_public_value,
            "CumulTestCost": compute_cumul_testing_cost,
            "Rt": compute_eff_reprod_number,
            "Employed": compute_employed,
            "Unemployed": compute_unemployed,
            "Tested": compute_tested,
            "Traced": compute_traced,
            "Cumul_Vaccine_Cost": compute_cumul_vaccination_cost,
            "Cumul_Cost": compute_total_cost
        }

        # This is also part of the summary
        model_reporters_dict = {
                "Step": compute_stepno,
                "N": compute_num_agents,
                "Isolated": compute_isolated,
                "Vaccinated" : compute_vaccinated,
                "Vaccines" : compute_vaccine_count,
                "V": compute_vaccinated,
                "Data_Time" : compute_datacollection_time,
                "Step_Time" : compute_step_time,
                "Generally_Infected": compute_generally_infected,
                "Fully_Vaccinated" : compute_fully_vaccinated_count,
                "Vaccine_1" : compute_vaccinated_1,
                "Vaccine_2" : compute_vaccinated_2,
                "Vaccine_Willing": compute_willing_agents,
        }
        #model_reporters_dict.update(processes_dict)
        model_reporters_dict.update(agent_status_dict)
        model_reporters_dict.update(age_vaccination_dict)
        model_reporters_dict.update(vaccinated_status_dict)
        model_reporters_dict.update(variant_data_collection_dict)
        model_reporters_dict.update(prices_dict)


        self.datacollector = DataCollector(model_reporters = model_reporters_dict)

        # Final step: infect an initial proportion of random agents
        num_init = int(self.num_agents * prop_initial_infected)

        # Save all initial values of agents in the database
        # Commit

        cumul_priv_value = compute_cumul_private_value(self)
        cumul_publ_value = compute_cumul_public_value(self)
        cumul_test_cost = compute_cumul_testing_cost(self)
        rt = compute_eff_reprod_number(self)
        employed = compute_employed(self)
        unemployed = compute_unemployed(self)
        tested = compute_tested(self)
        traced = compute_traced(self)
        cumul_vaccine_cost = compute_cumul_vaccination_cost(self)
        cumul_cost =compute_total_cost(self)
        step = compute_stepno(self)
        n = compute_num_agents(self)
        isolated = compute_isolated(self)
        vaccinated = compute_vaccinated(self)
        vaccines = compute_vaccine_count(self)
        v = compute_vaccinated(self)
        data_time = compute_datacollection_time(self)
        step_time = compute_step_time(self)
        generally_infected = compute_generally_infected(self)
        fully_vaccinated = compute_generally_infected(self)
        vaccine_1 = compute_vaccinated_1(self)
        vaccine_2 = compute_vaccinated_2(self)
        vaccine_willing = compute_willing_agents(self)


        #Save all initial summaries into the database
        # insert a summary into database
        myid = str(uuid.uuid4())
        summary_params = [(
            myid,
            cumul_priv_value,
            cumul_publ_value,
            cumul_test_cost,
            rt,
            employed,
            unemployed,
            tested,
            traced,
            cumul_vaccine_cost,
            cumul_cost,
            step,
            n,
            isolated,
            vaccinated,
            vaccines,
            v,
            data_time,
            step_time,
            generally_infected,
            fully_vaccinated,
            vaccine_1,
            vaccine_2,
            vaccine_willing
        )]

        self.db.insert_summary(summary_params)
        self.db.commit()


        for a in self.schedule.agents:
            if num_init < 0:
                break
            else:
                a.stage = Stage.EXPOSED
                self.model_data.generally_infected = self.model_data.generally_infected + 1
                num_init = num_init - 1

    def step(self):
        datacollectiontimeA = timeit.default_timer()
        self.datacollector.collect(self)
        # summary
        datacollectiontimeB = timeit.default_timer()
        self.datacollection_time = datacollectiontimeB-datacollectiontimeA

        steptimeA = timeit.default_timer()
        if self.stepno % self.model_data.dwell_15_day == 0:
            print(f'Simulating day {self.stepno // self.model_data.dwell_15_day}')
                #Addition for adding the daily amount of vaccines.
            if self.model_data.vaccination_now:
                self.model_data.vaccine_count = self.model_data.vaccine_count + self.model_data.distribution_rate

        # Deactivate unnecessary policies once they run their course
        self.policy_handler.reverse_dispatch(self, self.model_data)

        # Use the policy handler to apply relevant policies
        self.policy_handler.dispatch(self, self.model_data)

        # Activate contact tracing only if necessary and turn it off correspondingly at the end
        if not(self.model_data.tracing_now) and (self.stepno >= self.model_data.tracing_start):
            self.model_data.tracing_now = True
        
        if self.model_data.tracing_now and (self.stepno > self.model_data.tracing_end):
            self.model_data.tracing_now = False

        if not (self.model_data.vaccination_now) and (self.stepno >= self.model_data.vaccination_start):
            self.model_data.vaccinating_now = True

        if self.model_data.vaccination_now and (self.stepno > self.model_data.vaccination_end):
            self.model_data.vaccination_now = False


        for variant in self.model_data.variant_start_times:
            #print(f"Made it here for variant {variant} stepnumber is {self.stepno} out of {self.variant_start_times[variant]}")
            if not(self.model_data.variant_start[variant]) and (self.stepno > self.model_data.variant_start_times[variant]):
                new_infection_count = int(self.num_agents*self.model_data.prop_initial_infected)
                self.model_data.variant_start[variant] = True
                print(f"Variant {variant} is set to True with cound {new_infection_count}")
                for _ in range(0,new_infection_count):
                    print(f"Creating new variant {variant}")
                    #Creates new agents that are infected with the variant
                    ag = random.choice(list(AgeGroup))
                    sg = random.choice(list(SexGroup))
                    mort = self.model_data.age_mortality[ag]*self.model_data.sex_mortality[sg]
                    a = CovidAgent(self.i, ag, sg, mort, self)
                    self.schedule.add(a)
                    a.variant = variant
                    a.stage = Stage.EXPOSED
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    self.grid.place_agent(a, (x, y))
                    self.i = self.i + 1
                    self.num_agents = self.num_agents + 1
                    self.model_data.generally_infected += 1
                   



                # If new agents enter the population, create them
        if (self.stepno >= self.model_data.new_agent_start) and (self.stepno < self.model_data.new_agent_end):
            # Check if the current step is in the new-agent time map
            if self.stepno in self.new_agent_time_map.keys():
                # We repeat the following procedure as many times as the value stored in the map

                for _ in range(0, self.new_agent_time_map[self.stepno]):
                    # Generate an age group at random using a Poisson distribution centered at the mean
                    # age for the incoming population
                    in_range = False
                    arange = 0

                    while not(in_range):
                        arange = poisson_rvs(self.model_data.new_agent_age_mean)
                        if arange in range(0, 9):
                            in_range = True
                    
                    ag = AgeGroup(arange)
                    sg = random.choice(list(SexGroup))
                    mort = self.model_data.age_mortality[ag]*self.model_data.sex_mortality[sg]
                    a = CovidAgent(self.i, ag, sg, mort, self)
                    
                    # Some will be infected
                    if bernoulli_rvs(self.model_data.new_agent_prop_infected):
                        a.stage = Stage.EXPOSED
                        self.model_data.generally_infected = self.model_data.generally_infected + 1

                    self.schedule.add(a)
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    self.grid.place_agent(a, (x,y))
                    self.i = self.i + 1
                    self.num_agents = self.num_agents + 1
                    self.dwell_time_at_locations[(x,y)] += a.agent_data.dwelling_time

        
        self.schedule.step()
        steptimeB = timeit.default_timer()
        self.step_time = steptimeB - steptimeA

        # Commit (save first all the agent data in memory)
        # Save the summaries

        # We now do a reverse dispatch: deactivate all policies that need to be deactivated
        # 

        self.stepno = self.stepno + 1


