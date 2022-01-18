# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
import timeit
import time as tim
import mesa.batchrunner
from mesa import Agent, Model
from mesa.time import RandomActivation
from space_local import MultiGrid
from datacollection import DataCollector
from scipy.stats import poisson, bernoulli
from enum import Enum
import numpy as np
import random
import random
import sys
import psutil as psu
import timeit as time
import os
import pandas as pd
from functools import partial
import types
from dataclasses import dataclass

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

    def __init__(self, model, parameters):
        super().__init__(parameters[0], model)
        if len(parameters)<5:
            self.stage = Stage.SUSCEPTIBLE
            self.age_group = parameters[1]
            self.sex_group = parameters[2]
            self.vaccine_willingness = bernoulli.rvs(self.model.vaccination_percent)
            # These are fixed values associated with properties of individuals
            self.incubation_time = poisson.rvs(model.avg_incubation)
            self.dwelling_time = poisson.rvs(model.avg_dwell)
            self.recovery_time = poisson.rvs(model.avg_recovery)
            self.prob_contagion = self.model.prob_contagion_base
            # Mortality in vulnerable population appears to be around day 2-3
            self.mortality_value = parameters[3]
            # Severity appears to appear after day 5
            self.severity_value = model.prob_severe/(self.model.dwell_15_day*self.recovery_time)
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
            self.tracing_delay = 2*model.dwell_15_day
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
            for variant in self.model.variant_data_list:
                self.variant_immune[variant] = False
        else:
            self.stage = parameters[1]
            self.age_group = parameters[2]
            self.sex_group = parameters[3]
            self.vaccine_willingness = parameters[4]
            # These are fixed values associated with properties of individuals
            self.incubation_time = parameters[5]
            self.dwelling_time = parameters[6]
            self.recovery_time = parameters[7]
            self.prob_contagion = parameters[8]
            # Mortality in vulnerable population appears to be around day 2-3
            self.mortality_value = parameters[9]
            # Severity appears to appear after day 5
            self.severity_value = parameters[10]
            self.curr_dwelling = parameters[11]
            self.curr_incubation = parameters[12]
            self.curr_recovery = parameters[13]
            self.curr_asymptomatic = parameters[14]
            # Isolation measures are set at the model step level
            self.isolated = parameters[15]
            self.isolated_but_inefficient = parameters[16]
            # Contagion probability is local
            self.test_chance = parameters[17]
            # Horrible hack for isolation step
            self.in_isolation = parameters[18]
            self.in_distancing = parameters[19]
            self.in_testing = parameters[20]
            self.astep = parameters[21]
            self.tested = parameters[22]
            self.occupying_bed = parameters[23]
            # Economic assumptions
            self.cumul_private_value = parameters[24]
            self.cumul_public_value = parameters[25]
            # Employment
            self.employed = parameters[26]
            # Contact tracing: this is only available for symptomatic patients
            self.tested_traced = parameters[27]
            # All agents
            self.contacts = parameters[28]
            # We assume it takes two full days
            self.tracing_delay = parameters[29]
            self.tracing_counter = parameters[30]
            # vaccination variables
            self.vaccinated = parameters[31]
            self.safetymultiplier = parameters[32]
            self.current_effectiveness = parameters[33]
            self.vaccination_day = parameters[34]
            self.vaccine_count = parameters[35]
            self.dosage_eligible = parameters[36]
            self.fully_vaccinated =  parameters[37]
            self.variant = parameters[38]
            self.variant_immune = parameters[39]


    def alive(self):
        print(f'{self.unique_id} {self.age_group} {self.sex_group} is alive')

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

    # A function that applies a contact tracing test
    def test_contact_trace(self):
        # We may have an already tested but it had a posterior contact and became infected
        if self.stage == Stage.SUSCEPTIBLE:
            self.tested_traced = True
        elif self.stage == Stage.EXPOSED:
            self.tested_traced = True

            if bernoulli.rvs(self.model.prob_asymptomatic):
                    self.stage = Stage.ASYMPDETECTED
            else:
                self.stage = Stage.SYMPDETECTED
        elif self.stage == Stage.ASYMPTOMATIC:
            self.stage = Stage.ASYMPDETECTED
            self.tested_traced = True
        else:
            return

    def add_contact_trace(self, other):
        if self.model.tracing_now:
            self.contacts.add(other)

    #helper function that reveals if an agent is vaccinated
    def is_vaccinated(self):
        return self.vaccinated


    #Vaccination decision process, prone to change to find the ideal method.
    #Implementing the standard set that those who are older will be prioritized.
    #For now implementing random vaccination.

    def general_vaccination_chance(self):
        eligible_count = compute_age_group_count(self.model, self.age_group)
        vaccination_chance = 1/eligible_count
        if self.stage == Stage.ASYMPTOMATIC or self.stage == Stage.SUSCEPTIBLE or self.stage == Stage.EXPOSED:
            if bernoulli.rvs(vaccination_chance):
                return True
            return False
        return False

    def should_be_vaccinated(self):
        if self.general_vaccination_chance():
            if self.age_group == AgeGroup.C80toXX and self.model.vaccination_stage == VaccinationStage.C80toXX:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C70to79 and self.model.vaccination_stage == VaccinationStage.C70to79:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C60to69 and self.model.vaccination_stage == VaccinationStage.C60to69:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C50to59 and self.model.vaccination_stage == VaccinationStage.C50to59:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C40to49 and self.model.vaccination_stage == VaccinationStage.C40to49:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C30to39 and self.model.vaccination_stage == VaccinationStage.C30to39:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C20to29 and self.model.vaccination_stage == VaccinationStage.C20to29:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C10to19 and self.model.vaccination_stage == VaccinationStage.C10to19:
                update_vaccination_stage(self.model)
                return True
            elif self.age_group == AgeGroup.C00to09 and self.model.vaccination_stage == VaccinationStage.C00to09:
                update_vaccination_stage(self.model)
                return True
            else :
                update_vaccination_stage(self.model)
                return False
        return False

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


        #Implementing the vaccine
        #Will process based on whether all older agents in an older group are vaccinated
        if (not(self.vaccinated) or self.dosage_eligible) and self.model.vaccinating_now and (not(self.fully_vaccinated) and (self.vaccine_count < self.model.vaccine_dosage)):
            if self.should_be_vaccinated() and self.model.vaccine_count > 0 and self.vaccine_willingness:
                if not (bernoulli.rvs(0.1)):  # Chance that someone doesnt show up for the vaccine/ vaccine expires.
                    self.vaccinated = True
                    self.vaccination_day = self.model.stepno
                    self.vaccine_count = self.vaccine_count + 1
                    self.dosage_eligible = False
                    self.model.vaccine_count = self.model.vaccine_count - 1
                    self.model.vaccinated_count = self.model.vaccinated_count + 1

                else:
                    other_agent = self.random.choice(self.model.schedule.agents)
                    while not(other_agent.dosage_eligible and other_agent.vaccine_willingness):
                        other_agent = self.random.choice(self.model.schedule.agents)
                    other_agent.vaccinated = True
                    other_agent.vaccination_day = self.model.stepno
                    other_agent.vaccine_count = other_agent.vaccine_count +1
                    other_agent.dosage_eligible = False
                    self.model.vaccinated_count = self.model.vaccinated_count + 1
                    self.model.vaccine_count = self.model.vaccine_count - 1


        # Self isolation is tricker. We only isolate susceptibles, incubating and asymptomatics
        if not(self.in_isolation):
            if (self.astep >= self.model.isolation_start):
                if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.EXPOSED) or \
                    (self.stage == Stage.ASYMPTOMATIC):
                    if bool(bernoulli.rvs(self.model.isolation_rate)):
                        self.isolated = True
                    else:
                        self.isolated = False
                    self.in_isolation = True
            elif (self.astep >= self.model.isolation_end):
                if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.EXPOSED) or \
                    (self.stage == Stage.ASYMPTOMATIC):
                    if bool(bernoulli.rvs(self.model.after_isolation)):
                        self.isolated = True
                    else:
                        self.isolated = False
                    self.in_isolation = True

                    
        # Using a similar logic, we remove isolation for all relevant agents still locked
        if self.in_isolation and (self.astep >= self.model.isolation_end):
            if (self.stage == Stage.SUSCEPTIBLE) or (self.stage == Stage.EXPOSED) or \
                (self.stage == Stage.ASYMPTOMATIC):
                self.isolated = False
                self.in_isolation = False


        #Implementing the current safety factor for maximum effectiveness

        vaccination_time = self.model.stepno - self.vaccination_day
        #In this model I will assume that the vaccine is only half as effective once 2 weeks have passed given one dose.
        effective_date = self.model.dwell_15_day * 14
        if (vaccination_time < effective_date) and self.vaccinated == True:
            self.safetymultiplier = 1 - (self.model.effectiveness_per_dosage * (vaccination_time/effective_date)) - self.current_effectiveness #Error the vaccination will go to 0 once it is done.
        else:
            self.current_effectiveness = self.model.effectiveness_per_dosage * self.vaccine_count
            self.safetymultiplier = 1 - self.current_effectiveness * self.model.variant_data_list[self.variant]["Vaccine_Multiplier"]
            if (self.vaccine_count < self.model.vaccine_dosage):
                self.dosage_eligible = True  # Once this number is false, the person is eligible and is not fully vaccinated.
            elif self.fully_vaccinated == False:
                self.dosage_eligible = False
                self.fully_vaccinated = True
                self.model.fully_vaccinated_count = self.model.fully_vaccinated_count + 1


        # Using the model, determine if a susceptible individual becomes infected due to
        # being elsewhere and returning to the community
        if self.stage == Stage.SUSCEPTIBLE:
            #             if bernoulli.rvs(self.model.rate_inbound):
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
            if not(self.tested or self.tested_traced) and bernoulli.rvs(self.test_chance):
                self.tested = True
                self.model.cumul_test_cost = self.model.cumul_test_cost + self.model.test_cost
            # First opportunity to get infected: contact with others
            # in near proximity
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            infected_contact = 0 #Changed to account for asymptomatic threat of infection

            # Isolated people should only be contagious if they do not follow proper
            # shelter-at-home measures

            #Future implementaions would allow for multiple strains of the virus to stack on top of the same agent if exposed more than once but there is not much research showing what would really happen or what
            #values we would have to account for
            variant = "Standard"
            for c in cellmates:
                    if c.is_contagious() and (c.stage == Stage.SYMPDETECTED or c.stage == Stage.SEVERE) and self.variant_immune[c.variant] == False:
                        c.add_contact_trace(self)
                        if self.isolated: #If the agent is isolating
                            if bernoulli.rvs(1 - self.model.prob_isolation_effective):#Checks if isolation was effective
                                self.isolated_but_inefficient = True
                                infected_contact = 1
                                variant = c.variant
                                break
                            else:
                                self.isolated_but_inefficient = False
                        else: #If the agent is not isolating they come in contact
                            infected_contact = 1
                            variant = c.variant
                            break
                    elif c.is_contagious() and (c.stage == Stage.ASYMPTOMATIC or c.stage == Stage.ASYMPDETECTED) and self.variant_immune[c.variant] == False:
                        c.add_contact_trace(self)
                        if self.isolated:
                            if bernoulli.rvs(1 - self.model.prob_isolation_effective):#Checks if isolation was effective
                                self.isolated_but_inefficient = True
                                infected_contact = 2
                                variant = c.variant
                                #Does not break to check if there was a symptomatic contact in the same check
                            else:
                                self.isolated_but_inefficient = False
                        else:
                            infected_contact = 2
                            variant = c.variant

            # Value is computed before infected stage happens
            isolation_private_divider = 1
            isolation_public_divider = 1


            if self.employed:
                if self.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01


                self.cumul_private_value = self.cumul_private_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.SUSCEPTIBLE])*isolation_private_divider
                self.cumul_public_value = self.cumul_public_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SUSCEPTIBLE])*isolation_public_divider
            else:
                self.cumul_private_value = self.cumul_private_value + 0
                self.cumul_public_value = self.cumul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SUSCEPTIBLE]


            current_prob = self.prob_contagion * self.model.variant_data_list[variant]["Contagtion_Multiplier"]
            if self.vaccinated:
                current_prob = current_prob * self.safetymultiplier

            if infected_contact == 2:
                current_prob = current_prob * 0.42

            if infected_contact > 0:
                if self.isolated:
                    if bernoulli.rvs(current_prob) and not(bernoulli.rvs(self.model.prob_isolation_effective)):
                        self.stage = Stage.EXPOSED
                        self.variant = variant
                        self.model.generally_infected = self.model.generally_infected + 1
                else:
                    if bernoulli.rvs(current_prob):
                        #Added vaccination account after being exposed to determine exposure.
                        self.stage = Stage.EXPOSED
                        self.variant = variant
                        self.model.generally_infected = self.model.generally_infected + 1


            # Second opportunity to get infected: residual droplets in places
            # TODO

            if not(self.isolated):
                self.move()
        elif self.stage == Stage.EXPOSED:
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
                
                self.cumul_private_value = self.cumul_private_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.EXPOSED])*isolation_private_divider
                self.cumul_public_value = self.cumul_public_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.EXPOSED])*isolation_public_divider
            else:
                self.cumul_private_value = self.cumul_private_value + 0
                self.cumul_public_value = self.cumul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.EXPOSED]

            # Assignment is less expensive than comparison
            do_move = True

            current_prob_asymptomatic = self.model.prob_asymptomatic * self.model.variant_data_list[self.variant]["Asymtpomatic_Multiplier"]
            if self.vaccinated:
                current_prob_asymptomatic = 1-(1-self.model.prob_asymptomatic) * self.safetymultiplier #Probability of asymptomatic becomes 1-(probability of symptomatic)*safety_multiplier


            # If testing is available and the date is reached, test
            if not(self.tested or self.tested_traced) and bernoulli.rvs(self.test_chance):
                if bernoulli.rvs(current_prob_asymptomatic):
                    self.stage = Stage.ASYMPDETECTED
                else:
                    self.stage = Stage.SYMPDETECTED
                    do_move = False
                
                self.tested = True
                self.model.cumul_test_cost = self.model.cumul_test_cost + self.model.test_cost
            else:
                if self.curr_incubation < self.incubation_time:
                    self.curr_incubation = self.curr_incubation + 1
                else:
                    if bernoulli.rvs(current_prob_asymptomatic):
                        self.stage = Stage.ASYMPTOMATIC
                    else:
                        self.stage = Stage.SYMPDETECTED
                        do_move = False

            # Now, attempt to move
            if do_move and not(self.isolated):
                self.move()
            
            # Perform the move once the condition has been determined
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
                
                    self.cumul_private_value = self.cumul_private_value + \
                        ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.ASYMPTOMATIC])*isolation_private_divider
                    self.cumul_public_value = self.cumul_public_value + \
                        ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPTOMATIC])*isolation_public_divider
                else:
                    self.cumul_private_value = self.cumul_private_value + 0
                    self.cumul_public_value = self.cumul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPTOMATIC]

            if not(self.tested or self.tested_traced) and bernoulli.rvs(self.test_chance):
                self.stage = Stage.ASYMPDETECTED
                self.tested = True
                self.model.cumul_test_cost = self.model.cumul_test_cost + self.model.test_cost

            if self.curr_recovery >= self.recovery_time:
                self.stage = Stage.RECOVERED
                self.variant_immune[self.variant] = True
            else:
                self.curr_recovery  += 1

            if not (self.isolated):
                self.move()

                    
        elif self.stage == Stage.SYMPDETECTED:
            # Once a symptomatic patient has been detected, it does not move and starts
            # the road to severity, recovery or death. We assume that, by reaching a health
            # unit, they are tested as positive.
            self.isolated = True
            self.tested = True

            current_severe_chance = self.mortality_value * self.model.variant_data_list[self.variant]["Mortality_Multiplier"] * (1/(self.model.dwell_15_day))
            if (self.vaccinated):
                current_severe_chance = current_severe_chance * self.safetymultiplier


            # Contact tracing logic: use a negative number to indicate trace exhaustion
            if self.model.tracing_now and self.tracing_counter >= 0:
                # Test only when the count down has been reached
                if self.tracing_counter == self.tracing_delay:
                    for t in self.contacts:
                        t.test_contact_trace()

                    self.tracing_counter = -1
                else:
                    self.tracing_counter = self.tracing_counter + 1
            
            self.cumul_private_value = self.cumul_private_value + \
                self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.SYMPDETECTED]
            self.cumul_public_value = self.cumul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SYMPDETECTED]

            if self.curr_incubation + self.curr_recovery < self.incubation_time + self.recovery_time:
                self.curr_recovery = self.curr_recovery + 1

                if bernoulli.rvs(current_severe_chance):
                    self.stage = Stage.SEVERE
            else:
                self.stage = Stage.RECOVERED
                self.variant_immune[self.variant] = True
        elif self.stage == Stage.ASYMPDETECTED:
            self.isolated = True

            # Contact tracing logic: use a negative number to indicate trace exhaustion
            if self.model.tracing_now and self.tracing_counter >= 0:
                # Test only when the count down has been reached
                if self.tracing_counter == self.tracing_delay:
                    for t in self.contacts:
                        t.test_contact_trace()

                    self.tracing_counter = -1
                else:
                    self.tracing_counter = self.tracing_counter + 1

            self.cumul_private_value = self.cumul_private_value + \
                self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.ASYMPDETECTED]
            self.cumul_public_value = self.cumul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.ASYMPDETECTED]

            # The road of an asymptomatic patients is similar without the prospect of death
            if self.curr_incubation + self.curr_recovery < self.incubation_time + self.recovery_time:
               self.curr_recovery = self.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
                self.variant_immune[self.variant] = True

        elif self.stage == Stage.SEVERE:            
            self.cumul_private_value = self.cumul_private_value + \
                self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.SEVERE]
            self.cumul_public_value = self.cumul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.SEVERE]

            # Severe patients are in ICU facilities
            if self.curr_recovery < self.recovery_time:
                # Not recovered yet, may pass away depending on prob.
                if self.model.bed_count > 0 and self.occupying_bed == False:
                    self.occupying_bed = True
                    self.model.bed_count -= 1
                if self.occupying_bed == False:
                    if bernoulli(1/(self.recovery_time)): #Chance that someone dies at this stage is current_time/time that they should recover. This ensures that they may die at a point during recovery.
                        self.stage = Stage.DECEASED
                # else:
                #     if bernoulli(0 * 1/self.recovery_time): #Chance that someone dies on the bed is 42% less likely so I will also add that they have a 1/recovery_time chance of dying
                #         self.stage = Stage.DECEASED
                #         self.occupying_bed == False
                #         self.model.bed_count += 1
                self.curr_recovery = self.curr_recovery + 1
            else:
                self.stage = Stage.RECOVERED
                self.variant_immune[self.variant] = True
                if (self.occupying_bed == True):
                    self.occupying_bed == False
                    self.model.bed_count += 1



        elif self.stage == Stage.RECOVERED:
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            
            if self.employed:
                isolation_private_divider = 1
                isolation_public_divider = 1

                if self.isolated:
                    isolation_private_divider = 0.3
                    isolation_public_divider = 0.01

                self.cumul_private_value = self.cumul_private_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.RECOVERED])*isolation_private_divider
                self.cumul_public_value = self.cumul_public_value + \
                    ((len(cellmates) - 1) * self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.RECOVERED])*isolation_public_divider
            else:
                self.cumul_private_value = self.cumul_private_value + 0
                self.cumul_public_value = self.cumul_public_value - 2*self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.RECOVERED]


            # A recovered agent can now move freely within the grid again
            self.curr_recovery = 0
            self.isolated = False
            self.isolated_but_inefficient = False

            infected_contact = 0
            variant = "Standard"

            for c in cellmates:
                    if c.is_contagious() and self.model.variant_data_list[c.variant]["Reinfection"] == True and (c.stage == Stage.SYMPDETECTED or c.stage == Stage.SEVERE) and self.variant_immune[c.variant] == False:
                        c.add_contact_trace(self)
                        if self.isolated: #If the agent is isolating
                            if bernoulli.rvs(1 - self.model.prob_isolation_effective):#Checks if isolation was effective
                                self.isolated_but_inefficient = True
                                infected_contact = 1
                                variant = c.variant
                                break
                            else:
                                self.isolated_but_inefficient = False
                        else: #If the agent is not isolating they come in contact
                            infected_contact = 1
                            variant = c.variant
                            break
                    elif c.is_contagious() and (c.stage == Stage.ASYMPTOMATIC or c.stage == Stage.ASYMPDETECTED) and self.variant_immune[c.variant] == False:
                        c.add_contact_trace(self)
                        if self.isolated:
                            if bernoulli.rvs(1 - self.model.prob_isolation_effective):#Checks if isolation was effective
                                self.isolated_but_inefficient = True
                                infected_contact = 2
                                variant = c.variant
                                #Does not break to check if there was a symptomatic contact in the same check
                            else:
                                self.isolated_but_inefficient = False
                        else:
                            infected_contact = 2
                            variant = c.variant

            current_prob = self.prob_contagion * self.model.variant_data_list[variant]["Contagtion_Multiplier"]
            if self.vaccinated:
                current_prob = current_prob * self.safetymultiplier

            if infected_contact == 2:
                current_prob = current_prob * 0.42

            if infected_contact > 0:
                if self.isolated:
                    if bernoulli.rvs(current_prob) and not (bernoulli.rvs(self.model.prob_isolation_effective)):
                        if self.unique_id == 0:
                            print("Agent got infected here")
                        self.stage = Stage.EXPOSED
                        self.variant = variant
                else:
                    if bernoulli.rvs(current_prob):
                        if self.unique_id == 0:
                            print("Agent got infected here")
                        # Added vaccination account after being exposed to determine exposure.
                        self.stage = Stage.EXPOSED
                        self.variant = variant


            self.move()
        elif self.stage == Stage.DECEASED:
            self.cumul_private_value = self.cumul_private_value + \
                self.model.stage_value_dist[ValueGroup.PRIVATE][Stage.DECEASED]
            self.cumul_public_value = self.cumul_public_value + \
                self.model.stage_value_dist[ValueGroup.PUBLIC][Stage.DECEASED]
        else:
            # If we are here, there is a problem 
            sys.exit("Unknown stage: aborting.")

        self.astep = self.astep + 1

    def move(self):
        method = 1
        if method == 0:
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

        elif method == 1:#Distinguishing the methods for agent movements by coded parameter above.
            x ,y = self.pos
            movement_options = self.model.grid.movement_options[x][y]
            choice = random.choices(movement_options[0], weights=tuple(movement_options[1]), k=1)
            choice = choice[0]
            new_x = x + choice[0]
            new_y = y + choice[1]
            self.model.grid.move_agent(self, (new_x, new_y))



########################################

def compute_variant_stage(model, variant, stage):
    count = 0
    for agent in model.schedule.agents:
        if stage == Stage.SUSCEPTIBLE:
            if agent.variant == variant:
                count += 1
        else:
            if agent.stage == stage and agent.variant == variant:
                count += 1
    return count

def compute_vaccinated_stage(model, stage):
    count = 0
    for agent in model.schedule.agents:
        if agent.stage == stage and agent.vaccinated == True:
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
        if agent.isolated:
            count = count + 1
    return count

def compute_employed(model):
    count = 0
    for agent in model.schedule.agents:
        if agent.employed:
            count = count + 1

    return count

def compute_unemployed(model):
    count = 0

    for agent in model.schedule.agents:
        if not(agent.employed):
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
        value = value + agent.cumul_private_value
    return np.sign(value)*np.power(np.abs(value), model.alpha_private)/model.num_agents

def compute_cumul_public_value(model):
    value = 0

    for agent in model.schedule.agents:
        value = value + agent.cumul_public_value

    return np.sign(value)*np.power(np.abs(value), model.alpha_public)/model.num_agents


#  Changed the method for calculating the test cost. This will occur in more linear time,
#  can also differentiate being tested from being percieved as infected. This will be a rising value,
#  will change testing to be based on necessity along with the vaccine.

def compute_cumul_testing_cost(model):
    return model.cumul_test_cost

def compute_cumul_vaccination_cost(model):
    return model.cumul_vaccine_cost

def compute_total_cost(model):
    return model.cumul_test_cost + model.cumul_vaccine_cost

def compute_tested(model):
    tested = 0

    for agent in model.schedule.agents:
        if agent.tested:
            tested = tested + 1

    return tested

# Added to track the number of vaccinated agents.
def compute_vaccinated(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.vaccinated:
            vaccinated_count = vaccinated_count + 1

    return vaccinated_count

def compute_vaccinated_count(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.vaccinated:
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count

def compute_vaccinated_1(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.vaccine_count == 1:
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count

def compute_vaccinated_2(model):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if agent.vaccine_count == 2:
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count

def compute_willing_agents(model):
    count = 0
    for agent in model.schedule.agents:
        if agent.vaccine_willingness:
            count = count + 1
    return count


# Another helper function to determine the vaccination of agents based on agegroup.
def compute_vaccinated_in_group_count(model,agegroup):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.vaccinated) and (agent.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count



def compute_vaccinated_in_group(model,agegroup):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.vaccinated) and (agent.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count


def compute_fully_vaccinated_in_group(model,agegroup):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.fully_vaccinated) and (agent.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count


def compute_vaccinated_in_group_percent_vaccine_count(model, agegroup, count):
    vaccinated_count = 0
    for agent in model.schedule.agents:
        if (agent.vaccine_count == count) and (agent.age_group == agegroup):
            vaccinated_count = vaccinated_count + 1
    return vaccinated_count


def cumul_effectiveness_per_group_vaccinated(model,agegroup):
    vaccinated_count = 0
    effectiveness = 0
    for agent in model.schedule.agents:
        if (agent.age_group == agegroup and agent.vaccinated == True):
            vaccinated_count = vaccinated_count + 1
            effectiveness += agent.safetymultiplier
    if (vaccinated_count > 0):
        return 1-(effectiveness / vaccinated_count)
    else:
        return 0

def cumul_effectiveness_per_group(model,agegroup):
    agent_count = 0
    effectiveness = 0
    for agent in model.schedule.agents:
        if (agent.age_group == agegroup):
            agent_count = agent_count + 1
            effectiveness += agent.safetymultiplier
    if (agent_count > 0):
        return 1-(effectiveness / agent_count)
    else:
        return 0

def compute_age_group_count(model,agegroup):
    count = 0
    for agent in model.schedule.agents:
        if agent.age_group == agegroup:
            count = count + 1
    return count

def compute_eligible_age_group_count(model,agegroup):
    count = 0
    for agent in model.schedule.agents:
        if (agent.age_group == agegroup) and (agent.stage == Stage.SUSCEPTIBLE or agent.stage == Stage.EXPOSED or agent.stage == Stage.ASYMPTOMATIC) and agent.dosage_eligible and agent.vaccine_willingness:
            count = count + 1
    return count


def update_vaccination_stage(model):
    initial_stage = model.vaccination_stage
    if compute_eligible_age_group_count(model, AgeGroup.C80toXX) < 1:
        model.vaccination_stage = VaccinationStage.C70to79
        if compute_eligible_age_group_count(model, AgeGroup.C70to79) < 1:
            model.vaccination_stage = VaccinationStage.C60to69
            if compute_eligible_age_group_count(model, AgeGroup.C60to69) < 1:
                model.vaccination_stage = VaccinationStage.C50to59
                if compute_eligible_age_group_count(model, AgeGroup.C50to59) < 1:
                    model.vaccination_stage = VaccinationStage.C40to49
                    if compute_eligible_age_group_count(model, AgeGroup.C40to49) < 1:
                        model.vaccination_stage = VaccinationStage.C30to39
                        if compute_eligible_age_group_count(model, AgeGroup.C30to39) < 1:
                            model.vaccination_stage = VaccinationStage.C20to29
                            if compute_eligible_age_group_count(model, AgeGroup.C20to29) < 1:
                                model.vaccination_stage = VaccinationStage.C10to19
                                if compute_eligible_age_group_count(model, AgeGroup.C10to19) < 1:
                                    model.vaccination_stage = VaccinationStage.C00to09
    else:
        model.vaccination_stage = VaccinationStage.C80toXX
    if initial_stage != model.vaccination_stage:
        print(f"Vaccination stage is now {model.vaccination_stage}")


def compute_willing_group_count(model, agegroup):
    count = 0
    for agent in model.schedule.agents:
        if(agent.vaccine_willingness):
            count += 1
    return count

def compute_traced(model):
    tested = 0

    for agent in model.schedule.agents:
        if agent.tested_traced:
            tested = tested + 1

    return tested


def compute_total_processor_usage(model):
    if model.stepno % model.dwell_15_day == 0:
        processes = psu.cpu_percent(1, True)
        process_count = 0
        for idx, process in enumerate(processes):
            if (process > 0.0):
                process_count = process_count + 1
        return process_count
    else:
        return 0

def compute_processor_usage(model, processoridx):
    if model.stepno % model.dwell_15_day == 0:
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
            exp_time = exp_time + agent.incubation_time
            prob_contagion = agent.prob_contagion
        elif agent.stage == Stage.SYMPDETECTED:
            # NOTE: this part needs to be adapted to model hospital transmission in further detail
            symptomatics = symptomatics + 1
            sympt_time = sympt_time + agent.incubation_time
            prob_contagion = agent.prob_contagion
        elif agent.stage == Stage.ASYMPTOMATIC:
            asymptomatics = asymptomatics + 1
            asympt_time = asympt_time + agent.incubation_time + agent.recovery_time
            prob_contagion = agent.prob_contagion
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
    return model.kmob * model.repscaling * prob_contagion * avg_contacts * infectious_period

def compute_num_agents(model):
    return model.num_agents

def compute_vaccine_count(model):
    return model.vaccine_count

def compute_datacollection_time(model):
    return model.datacollection_time

def compute_step_time(model):
    return model.step_time

def compute_generally_infected(model):
    return model.generally_infected

def compute_fully_vaccinated_count(model):
    return model.fully_vaccinated_count


def get_agent_data(agent, param_name):
    return agent.__dict__[param_name]

"""Generates a matrix containing directional vectors determining movement accross the 
    Input consists of a grid the same with dimensions (width x height) containing points with (pos,(dipole?, (vector or value)))
    Algorithm consists of iterating through each object within the input list and generating components of each part of the grid based on their components
"""

@dataclass
class Attraction_Item:
    pos: tuple #(x,y)
    dipole: bool
    #vector: list #normalized unit
    value: float #Magnitude

def generate_random_map(width, height):
    map = []
    for i in range(int(100)):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        value = random.randint(0, 100)
        map.append(Attraction_Item((x,y),False,value))
    print("Map Generated")
    return map

def normalize(vector): #Normalize N-D vector. Find a library for this as well.
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def find_theta(unit_vector):#Basically arctan of a vector w/r to a circle. Find in a library or something
    if len(unit_vector) != 2:
        raise IndexError("vector a expected to be length 2")
    x = unit_vector[0]
    y = unit_vector[1]
    rad = np.arctan2(y, x)
    degrees = np.int(rad*180/np.pi)
    if degrees < 0:
        degrees = 360 - degrees
    return degrees



def find_probability_2D(unit_vector):#Given a 2-D vector, find the probability of movement within a moore neighborhood of size 1.
    """ Conditions for a probability of 1 in each tile.
                    [[-0.5, 0.5],[0.0, 1.0],[0.5, 0.5]],
                    [[-1.0, 0.0],[0.0, 0.0],[1.0, 0.0]],
                    [[-0.5,-0.5],[0.0,-1.0],[0.5,-0.5]]   """
    adjacency = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    quarter_distance = np.sqrt(2)/2
    theta = find_theta(unit_vector)
    if unit_vector[0] >= 0:  # We are on the right hand side of the circle
        if unit_vector[1] >= 0:  # We are on the upper right half of the circle
            if unit_vector[1] >= quarter_distance:  # We are in octant 1
                adjacency[0][1] = (theta - 1 * 45)/ 45  # P(2)
                adjacency[0][2] = 1 - adjacency[0][1] # P(1)
            else:  # We are in octant 0
                adjacency[0][2] = (theta - 0 * 45) / 45 # P(1)
                adjacency[1][2] = 1 - adjacency[0][2] # P(0)

        else:  # We are on the bottom right
            if unit_vector[0] >= quarter_distance:  # We are in octant 7
                adjacency[2][2] = (theta - 360) / 45   # P(0)
                adjacency[1][2] = 1 - adjacency[2][2]  # P(7)
            else:  # We are in octant 6
                adjacency[2][1] = (theta - 360 - 1 * 45) / 45  # P(7)
                adjacency[2][2] = 1 - adjacency[2][1]  # P(6)


    else:  # We are on the left side
        if unit_vector[1] >= 0:  # We are on the uppper left half of the circle
            if unit_vector[1] >= quarter_distance:  # We are in octant 2
                adjacency[0][0] = (theta - 2 * 45) / 45   # P(3)
                adjacency[0][1] = 1 - adjacency[0][0]  # P(2)
            else:  # We are in octant 3
                adjacency[1][0] = (theta - 3 * 45) / 45   # P(4)
                adjacency[0][0] = 1 - adjacency[1][0]  # P(3)

        else:  # We are on the bottom left
            if unit_vector[1] >= (-1 * quarter_distance):  # We are in octant 4
                adjacency[1][0] = (theta - 360 - 3 * 45) / 45  # P(5)
                adjacency[2][0] = 1 - adjacency[1][0]  # P(4)
            else:  # We are in octant 5
                adjacency[2][0] = (theta - 360 - 2 * 45) / 45  # P(6)
                adjacency[2][1] = 1 - adjacency[2][0]  # P(5)

    return adjacency

def generate_vspace(input, width, height):
    space = []
    unit_space = []
    for x in range(width):
        col = []
        for y in range(height):
            col.append([0,0,0])#Third component being the current affinity value,  probability of keeping still relative to other vectors
        space.append(col)
        unit_space.append(col)

    """Generating vectors"""
    for item in input:
        for x in range(width):
            for y in range(height):
                x_, y_ = item.pos

                if item.dipole == False:  # If it is a unit charge
                    if x_ != x or y_ != y:
                        # Calculate vector between current point and the charge point for each point then normalize
                        # Peform the charge calculation based on the value for the magnitude and multiply
                        x_component = x_ - x
                        y_component = y_ - y
                        unit_vector = normalize([x_component,y_component])
                        distance = np.abs(x_component**2) + np.abs(y_component**2)
                        magnitude = item.value/distance
                        vector = unit_vector * magnitude
                        #Adding the effects of the vector with magnitude to the positional vector
                        space[x][y][0] += vector[0]
                        space[x][y][1] += vector[1]
                    else:
                        space[x][y][2] = item.value
                if item.dipole == True:
                    print("Not available yet")

    print("Vectors Generated")
    """Generating movement probabilities"""
    probability_space = []
    for x in range(width):
        col = []
        for y in range(height):
            if space[x][y][2] > 0: #We are on a source or sink we have a probability of staying on the current spot
                spac = space[x][y]
                unit_vector = normalize(space[x][y])
                unit_2D = normalize([unit_vector[0],unit_vector[1]])
                unit_space[x][y] = unit_2D
                direction = find_probability_2D(unit_2D)
                stationary_chance = np.abs(unit_vector[2] / (np.abs(unit_vector[0]) + np.abs(unit_vector[1]) + np.abs(unit_vector[2])))
                movement_chance = 1 - stationary_chance
                new_direction = []
                for row in direction:
                    new_row = []
                    for unit in row:
                        new_row.append(unit*movement_chance)
                    new_direction.append(new_row)
                new_direction[1][1] = stationary_chance
                # print(direction, new_direction, movement_chance)
                col.append(new_direction)

            else:
                unit_vector = normalize([space[x][y][0],space[x][y][1]])
                unit_space[x][y] = unit_vector
                direction = find_probability_2D(unit_vector)
                col.append(direction)
        probability_space.append(col)
    print("Probabilities Generated")
    return probability_space, unit_space



class CovidModel(Model):

    """ A model to describe parameters relevant to COVID-19"""
    def __init__(self, num_agents, width, height, kmob, repscaling, rate_inbound, age_mortality,
                 sex_mortality, age_distribution, sex_distribution, prop_initial_infected,
                 proportion_asymptomatic, proportion_severe, avg_incubation_time, avg_recovery_time, prob_contagion,
                 proportion_isolated, day_start_isolation, days_isolation_lasts, after_isolation, prob_isolation_effective, social_distance,
                 day_distancing_start, days_distancing_lasts, proportion_detected, day_testing_start, days_testing_lasts, 
                 new_agent_proportion, new_agent_start, new_agent_lasts, new_agent_age_mean, new_agent_prop_infected,
                 day_tracing_start, days_tracing_lasts, stage_value_matrix, test_cost, alpha_private, alpha_public, proportion_beds_pop, day_vaccination_begin,
                 day_vaccination_end, effective_period, effectiveness, distribution_rate, cost_per_vaccine, vaccination_percent, variant_data, step_count, load_from_file,
                 loading_file_path, starting_step, agent_storage, model_storage, agent_increment, model_increment, iteration, dummy=0):

        self.iteration = iteration
        self.max_steps  = step_count
        self.running = True
        self.starting_step = starting_step
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, True)
        #Testing the effect of adding a vector space to the grid
        #Generate map based on random input or systematic fashion to study the effect of a pandemic with known initial conditions.
        map = generate_random_map(width, height)
        self.vspace, self.unit_space = generate_vspace(map, self.grid.width, self.grid.height)#Generating the vector space following the dimensions of the grid
        self.grid.apply_vspace(self.vspace, self.unit_space)

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
        self.fully_vaccinated_count = 0
        self.bed_count = 0
        self.prop_initial_infected = prop_initial_infected
        self.generally_infected = 0 #Stores the number of generally infected agents, this value is updated at every state change within the model.

        #TODO in the future we will consider the costs of different policy measures.
        self.cumul_vaccine_cost = 0
        self.cumul_test_cost = 0
        self.total_costs = 0

        # Used for runtime over time analysis.
        self.datacollection_time = 0
        self.step_time = 0

        # temporary vaccination chance portion, will exclude when vaccination process is more clear.

        #Vaccination model variables:
        #TODO add a parameter list of vaccines like you did for the variants to have a more stochastic distribution of the vaccine.
        self.vaccination_chance = distribution_rate/num_agents #TODO study the vaccination process again to revise why you kept this

        #Vaccination information stored onto the model.
        self.vaccination_stage = VaccinationStage.C80toXX #Under the oldest to youngest priority model. Might change if we introduce occupations
        self.vaccine_cost = cost_per_vaccine #TODO remove this everywhere, it serves no purpose
        self.day_vaccination_begin = day_vaccination_begin
        self.day_vaccination_end = day_vaccination_end
        self.effective_period = effective_period #TODO We could implement an effective period for the vaccine if immunity dies over time. Requires more research
        self.effectiveness = effectiveness
        self.distribution_rate = distribution_rate
        self.vaccine_count = 0 #Stores the total number of vaccines available within the model.
        self.vaccinated_count = 0 #Stores the number of 1'st dose agents within the model.
        self.vaccination_percent = vaccination_percent #Percent of vaccine willing agents.

        # Keeps track of how many doses of the vaccine are required
        self.vaccine_dosage = 2 #TODO Make this an input parameter.
        self.effectiveness_per_dosage = self.effectiveness/self.vaccine_dosage

        #Variant variables within the model:
        #TODO work on a method for a self evolving variant instead of spontaniously generated variants.
        self.variant_data_list = {}
        #Storing all the parameters for each variant inside a dictionary.
        for variant in variant_data:
            self.variant_data_list[variant["Name"]] = {}
            self.variant_data_list[variant["Name"]]["Name"] = variant["Name"]
            self.variant_data_list[variant["Name"]]["Appearance"] = variant["Appearance"]
            self.variant_data_list[variant["Name"]]["Contagtion_Multiplier"] = variant["Contagtion_Multiplier"]
            self.variant_data_list[variant["Name"]]["Vaccine_Multiplier"] = variant["Vaccine_Multiplier"]
            self.variant_data_list[variant["Name"]]["Asymtpomatic_Multiplier"] = variant["Asymtpomatic_Multiplier"]
            self.variant_data_list[variant["Name"]]["Mortality_Multiplier"] = variant["Mortality_Multiplier"]
            self.variant_data_list[variant["Name"]]["Reinfection"] = variant["Reinfection"]

        #Backtracking model data:
        self.load_from_file = load_from_file #Dictates whether we will be loading the model from a save file.
        self.loading_file_path = loading_file_path #Details the location of the file to load the agents from.
        self.starting_step = starting_step #If we are loading from a file, details the starting step within the save file to load from.
        self.agent_storage = agent_storage #Details the method for storing the agent data. 0 -> We dont store agent data, 1->We store every step of the agent data, 2->We store incremental agent data, 3->We store final step agent data
        self.model_storage = model_storage #Details the method for storing the model data. 0 -> We dont store model data, 1->We store every step of the model data, 2->We store incremental model data, 3->We store final step model data
        self.iteration = iteration #Current iteration in the ensemble of iterations being run with the same scenario. Useful for running parallel backtracking jobs.

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

        self.model_reporters = {} #For using the model reporting feature in mesa or in the def step function.



        # Number of 15 minute dwelling times per day
        self.dwell_15_day = 96

        # Average dwelling units
        self.avg_dwell = 4

        # The average incubation period is 5 days, which can be changed
        self.avg_incubation = int(round(avg_incubation_time * self.dwell_15_day))

        # Probability of contagion after exposure in the same cell
        # Presupposes a person centered on a 1.8 meter radius square.
        # We use a proxy value to account for social distancing.
        # Representativeness modifies the probability of contagion by the scaling factor
        if repscaling < 2:
            self.repscaling = 1
        else:
            self.repscaling = (np.log(repscaling)/np.log(1.96587))

        self.prob_contagion_base = prob_contagion / self.repscaling

        # Mobility constant for geographic rescaling
        self.kmob = kmob

        # Proportion of daily incoming infected people from other places
        self.rate_inbound = rate_inbound/self.dwell_15_day

        # TODO Probability of contagion due to residual droplets: (Might be necessary for implementing networks and POI)
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

        # We need an additional variable to activate and inactivate automatic contact tracing
        self.tracing_start = day_tracing_start* self.dwell_15_day
        self.tracing_end = self.tracing_start + days_tracing_lasts*self.dwell_15_day
        self.tracing_now = False

        # Same for isolation rate
        self.isolation_rate = proportion_isolated
        self.isolation_start = day_start_isolation*self.dwell_15_day
        self.isolation_end = self.isolation_start + days_isolation_lasts*self.dwell_15_day
        self.after_isolation = after_isolation
        self.prob_isolation_effective = prob_isolation_effective

        # Same for social distancing
        self.distancing = social_distance
        self.distancing_start = day_distancing_start*self.dwell_15_day
        self.distancing_end = self.distancing_start + days_distancing_lasts*self.dwell_15_day

        # Introduction of new agents after a specific time
        self.new_agent_num = int(new_agent_proportion * self.num_agents)
        self.new_agent_start = new_agent_start*self.dwell_15_day
        self.new_agent_end = self.new_agent_start + new_agent_lasts*self.dwell_15_day
        self.new_agent_age_mean = new_agent_age_mean
        self.new_agent_prop_infected = new_agent_prop_infected

        #Code for vaccination
        self.vaccination_start = day_vaccination_begin * self.dwell_15_day
        self.vaccination_end = day_vaccination_end * self.dwell_15_day
        self.vaccinating_now = False
        # Closing of various businesses
        # TODO: at the moment, we assume that closing businesses decreases the dwell time.
        # A more proper implementation would a) use a power law distribution for dwell times
        # and b) assign a background of dwell times first, modifying them upwards later
        # for all cells.
        # Alternatively, shutting restaurants corresponds to 15% of interactions in an active day, and bars to a 7%
        # of those interactions

        #Initializing the start times for each spontaniously generated variant.
        self.variant_start_times = {}
        self.variant_start = {}
        for key in self.variant_data_list:
            self.variant_start_times[key] = self.variant_data_list[key]["Appearance"] * self.dwell_15_day
            self.variant_start[key] = False

        # Now, a neat python trick: generate the spacing of entries and then build a map
        times_list = list(np.linspace(self.new_agent_start, self.new_agent_end, self.new_agent_num, dtype=int))
        self.new_agent_time_map = {x:times_list.count(x) for x in times_list}

        # Probability of severity
        self.prob_severe = proportion_severe

        # Number of beds where saturation limit occurs
        self.max_beds_available = self.num_agents * proportion_beds_pop
        self.bed_count = self.max_beds_available

        # CREATING AGENTS
        self.i = 0
        if load_from_file == False: #If were creating a new model based on demographic data.
            for ag in self.age_distribution:
                for sg in self.sex_distribution:
                    r = self.age_distribution[ag]*self.sex_distribution[sg]
                    num_agents = int(round(self.num_agents*r))
                    mort = self.age_mortality[ag]*self.sex_mortality[sg]
                    for k in range(num_agents):
                        parameters = [self.i, ag, sg, mort]
                        a = CovidAgent(self, parameters)
                        self.schedule.add(a)
                        x = self.random.randrange(self.grid.width)
                        y = self.random.randrange(self.grid.height)
                        self.grid.place_agent(a, (x,y))
                        self.i = self.i + 1

        else: #If where creating a model from a previously generated model
            data_df = pd.read_csv(loading_file_path)
            #We could extract data from the loading file path name to find out what type of data we are looking at.
            #TODO provide a nomenclature to the saved agent files.
                #1->Complete, 2->Incremental, 3->Final
                #Use some regex magic to find these keywords within the file name
            for agent in range(self.num_agents):
                agent_data = []
                position = None

                #For each agent we look through the different parameter names we initialized earlier as the standard and begin appending values from the Dataframe into the agent initialization.
                for param_name in self.agent_parameter_names:

                    key = "Agent " + str(agent) + " " + param_name #Standard key nomenclature within the agent data file.

                    #Searching for the data at the defined step and iteration value we saved earlier through the batchrunner library folder.
                    #This allows for multiple models to be backtracked according to their associated iteration number.
                    #TODO Specify a situation where every iteration runs on a single iteration within the file.
                    #TODO Contemplate reality and how this backtracking thing will work
                    #Are we just backtracking from a specific scenario?
                    #Are we backtracking to extend the length of a model?
                    #If we are extending the length of a model we might as well just say that the iterations actually matter.
                    #If we are working from a specific model then we will have to specify this fact and we will have to input the desired iteration.
                    #TODO add two new parameters: load_file_iteration, load_specific_iteration -> True/False
                    #TODO if we are loading to extend the file then wouldnt we just be using the only step that exists?

                    value = data_df[key][data_df["Step"] == self.starting_step][data_df["Iteration"] == self.iteration]
                    value = value.item()

                    #Enums arent saved as enums in the dataframe so we will have to convert them here.
                    if (param_name == "stage"):
                        value = value.replace("Stage.", "")
                        value = Stage[value]
                    if (param_name == "age_group"):
                        value = value.replace("AgeGroup.", "")
                        value = AgeGroup[value]
                    if (param_name == "sex_group"):
                        value = value.replace("SexGroup.", "")
                        value = SexGroup[value]

                    #position is not an agent parameter but a model parameter.
                    if (param_name == 'pos'):
                        position = value
                    elif(param_name == "variant_immune"):
                        value = eval(value)#Dictionaries are saved as strings in the dataframe.
                        agent_data.append(value.copy())
                    else:
                        agent_data.append(value)

                #Create the agent based on the parameter list.
                a = CovidAgent(self ,agent_data)
                self.schedule.add(a)
                self.grid.place_agent(a, eval(position))


            print("Confirmation that the code works by finding the values and datatypes of the agent's variables: (Comment this block out if you are sure everythings working.)")
            agent = (self.schedule.agents)[0]
            for param_name in self.agent_parameter_names:
                if (param_name == 'model'):
                    continue
                value = get_agent_data(agent,param_name)


        #DECLARING ALL MODEL REPORTERS.

        #Wonky attempt at modelling CPU usage within the model.
        #TODO Delete everything related to this method. It literally freezes the model every time.
        processes = psu.cpu_percent(1, True)
        processes_dict = {}
        for idx, process in enumerate(processes):
            processor_name = "Processor " + str(idx)
            processes_dict[processor_name] = [compute_processor_usage, [self, idx]]
        processes_dict["Total_Processore_Use"] = compute_total_processor_usage

        #Reporting the different age group vaccination data.
        age_vaccination_dict = {}
        for age in AgeGroup:
            age_group_name = "Generally_Vaccinated " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_vaccinated_in_group, [self, age]]
            # age_group_name = "Cumulative_Effectiveness " + str(age.name)
            # age_vaccination_dict[age_group_name] = [cumul_effectiveness_per_group, [self, age]]
            age_group_name = "Fully_Vaccinated " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_fully_vaccinated_in_group, [self, age]]
            age_group_name = "Vaccinated_1 " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_vaccinated_in_group_percent_vaccine_count, [self, age, 1]]
            age_group_name = "Vaccinated_2 " + str(age.name)
            age_vaccination_dict[age_group_name] = [compute_vaccinated_in_group_percent_vaccine_count, [self, age, 2]]

        #Reporting the variant epidemic data.
        variant_data_collection_dict = {}
        for variant in variant_data:
            for stage in Stage:
                variant_stage_name = str(variant["Name"]) + str(stage.name)
                if stage == Stage.SUSCEPTIBLE: #Clever use of the name SUSCEPTIBLE as this makes no sense when someone has a variant.
                    variant_stage_name = str(variant["Name"])+"_Total_Infected"
                variant_data_collection_dict[variant_stage_name] = [compute_variant_stage, [self, variant["Name"], stage]]

        #For confirming that the vaccination values are working as intended.
        #TODO revisit this to find out how well the vaccinations are working.
        vaccinated_status_dict = {}
        for stage in Stage:
            stage_name = "Vaccinated_" + str(stage.name)
            vaccinated_status_dict[stage_name] = [compute_vaccinated_stage, [self, stage]]

        #Standard epidemic data.
        agent_status_dict = {}
        for stage in Stage:
            stage_name = str(stage.name)
            agent_status_dict[stage_name] = [compute_stage, [self,stage]]

        #Just some other things to include in the model report.
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
        general_reporters_dict = {
                "Step": compute_stepno,
                "N": compute_num_agents,
                "Isolated": compute_isolated,
                "Generally_Vaccinated" : compute_vaccinated,
                "Vaccines" : compute_vaccine_count,
                "Data_Time" : compute_datacollection_time,
                "Step_Time" : compute_step_time,
                "Generally_Infected": compute_generally_infected,
                "Fully_Vaccinated" : compute_fully_vaccinated_count,
                "Vaccine_1" : compute_vaccinated_1,
                "Vaccine_2" : compute_vaccinated_2,
                "Vaccine_Willing": compute_willing_agents,
        }

        model_reporters_dict = {}
        # model_reporters_dict.update(processes_dict)
        model_reporters_dict.update(general_reporters_dict)
        model_reporters_dict.update(agent_status_dict)
        model_reporters_dict.update(age_vaccination_dict)
        model_reporters_dict.update(vaccinated_status_dict)
        model_reporters_dict.update(variant_data_collection_dict)
        model_reporters_dict.update(prices_dict)

        self.datacollector = None
        self.model_reporters = model_reporters_dict
        self.model_vars = {}
        if(self.model_storage > 0): #We don't consider the ModelReporters method if were not tracking all the data across every step. And we create the equivalent here.
            for name, reporter in self.model_reporters.items():
                self.model_vars[name] = []

        elif(self.model_storage == -1):#Special case to use the traditional datacollector
            self.datacollector = DataCollector(model_reporters=model_reporters_dict, agent_reporters=None, tables=None)

        #For storing agent data we dont use ModelReporters at all, so we will have to do it ourselves when we reach the step(model). So we just initialize the reporters here
        self.agent_reporters = {}
        self.agent_vars = {}
        if(self.agent_storage > 0):
            for index, agent in enumerate(self.schedule.agents):  # Creates a column for each agent and parameter
                for param_name in self.agent_parameter_names:  # Retrieves the name of the parameters for that particular agent and adds it to the list of column headings. parameter_names will be a list of strings
                    key = "Agent " + str(index) + " " + param_name #Nomenclature for storing agent data.
                    self.agent_reporters[key] = [get_agent_data,[agent, param_name]]
                    self.agent_vars[key] = []




        #FINAL STEP: INFECT AN INITIAL PROPORTION OF RANDOM AGENTS
        num_init = int(self.num_agents * prop_initial_infected)

        if(load_from_file == False):#We don't reinfect agents if we are loading from a previous model.
            for a in self.schedule.agents:
                if num_init < 0:
                    break
                else:
                    #Shouldn't this be random? Or is it intentionally set to be the 0'th agent being infected every time.
                    a.stage = Stage.EXPOSED
                    self.generally_infected = self.generally_infected + 1
                    num_init = num_init - 1

    def retrieve_model_Data(self):
        return pd.DataFrame(self.model_vars)
    def retrieve_agent_Data(self):
        return pd.DataFrame(self.agent_vars)

    def step(self):
        #Collecting the data using the DataCollector() method in mesa and timing it for runtime analysis.
        data_time_A = timeit.default_timer()
        if (self.model_storage == -1 and self.schedule.steps < self.max_steps-1):
            self.datacollector.collect(self)

        # This is the equivalent to datacollector.collect(self) except it is done within the model.
        if (self.model_storage == 1 and self.schedule.steps < self.max_steps-1):
            for var, reporter in self.model_reporters.items():
                if isinstance(reporter, types.LambdaType):
                    self.model_vars[var].append(reporter(self))
                # Check if function with arguments
                elif isinstance(reporter, list):
                    self.model_vars[var].append(reporter[0](*reporter[1]))
        #Same thing is done for agent data.
        if(self.agent_storage == 1 and self.schedule.steps < self.max_steps-1):
            for var, reporter in self.agent_reporters.items():
                if isinstance(reporter, types.LambdaType):
                    self.agent_vars[var].append(reporter(self))
                # Check if function with arguments
                elif isinstance(reporter, list):
                    self.agent_vars[var].append(reporter[0](*reporter[1]))

        #If we are incrementally running the model then we will have to collect at the specified time interval.
        if(self.model_storage == 2 and self.schedule.steps < self.max_step-1):
            if(self.stepno % self.increment_value == 0):
                for var, reporter in self.model_reporters.items():
                    if isinstance(reporter, types.LambdaType):
                        self.model_vars[var].append(reporter(self))
                    # Check if function with arguments
                    elif isinstance(reporter, list):
                        self.model_vars[var].append(reporter[0](*reporter[1]))

        #We do the same for the agent data.
        if (self.agent_storage == 2 and self.schedule.steps < self.max_step-1   ):
            if (self.stepno % self.increment_value == 0):
                for var, reporter in self.agent_reporters.items():
                    if isinstance(reporter, types.LambdaType):
                        self.agent_vars[var].append(reporter(self))
                    # Check if function with arguments
                    elif isinstance(reporter, list):
                        self.agent_vars[var].append(reporter[0](*reporter[1]))

        data_time_B = timeit.default_timer()
        self.datacollection_time = data_time_B-data_time_A



        #Running the actual sauce of the step of the model and timing it for runtime analysis.
        step_time_A = timeit.default_timer()

        if self.stepno % self.dwell_15_day == 0:
            print(f'Simulating day {self.stepno // self.dwell_15_day}')
            #Adding vaccines at the beginning of every day in the model.
            if self.vaccinating_now:
                self.vaccine_count = self.vaccine_count + self.distribution_rate


        # Activate contact tracing only if necessary and turn it off correspondingly at the end
        if not(self.tracing_now) and (self.stepno >= self.tracing_start):
            self.tracing_now = True
        
        if self.tracing_now and (self.stepno > self.tracing_end):
            self.tracing_now = False

        if not (self.vaccinating_now) and (self.stepno >= self.vaccination_start):
            self.vaccinating_now = True

        if self.vaccinating_now and (self.stepno > self.vaccination_end):
            self.vaccinating_now = False


        #In the spontanious method for introducing variants we have new agents arrive that contain the variant.
        #For these new people coming in it will be interesting to see what their intentions are. Maybe they are just coming for a visit?
        for variant in self.variant_start_times:
            if not(self.variant_start[variant]) and (self.stepno > self.variant_start_times[variant]):
                new_infection_count = int(self.num_agents*self.prop_initial_infected)
                self.variant_start[variant] = True
                for _ in range(0,new_infection_count):
                    #Creates new agents that are infected with the variant
                    ag = random.choice(list(AgeGroup))
                    sg = random.choice(list(SexGroup))
                    mort = self.age_mortality[ag]*self.sex_mortality[sg]
                    a = CovidAgent([self.i, ag, sg, mort, self])
                    self.schedule.add(a)
                    a.variant = variant
                    a.stage = Stage.EXPOSED
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    self.grid.place_agent(a, (x, y))
                    self.i = self.i + 1
                    self.num_agents = self.num_agents + 1
                    self.generally_infected += 1



        # If new agents enter the population, create them
        if (self.stepno >= self.new_agent_start) and (self.stepno < self.new_agent_end):
            # Check if the current step is in the new-agent time map
            if self.stepno in self.new_agent_time_map.keys():
                # We repeat the following procedure as many times as the value stored in the map
                for _ in range(0, self.new_agent_time_map[self.stepno]):
                    # Generate an age group at random using a Poisson distribution centered at the mean
                    # age for the incoming population
                    in_range = False
                    arange = 0
                    while not(in_range):
                        arange = poisson.rvs(self.new_agent_age_mean)
                        if arange in range(0, 9):
                            in_range = True
                    ag = AgeGroup(arange)
                    sg = random.choice(list(SexGroup))
                    mort = self.age_mortality[ag]*self.sex_mortality[sg]
                    a = CovidAgent(self.i, ag, sg, mort, self)
                    # Some will be infected
                    if bernoulli.rvs(self.new_agent_prop_infected):
                        a.stage = Stage.EXPOSED
                        self.generally_infected = self.generally_infected + 1
                    self.schedule.add(a)
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    self.grid.place_agent(a, (x,y))
                    self.i = self.i + 1
                    self.num_agents = self.num_agents + 1

        #If we have reached the final step.
        if self.schedule.steps == self.max_steps-1:
            print(f"{self.schedule.steps} ::  {self.max_steps}  was the max step and we made it here")
            print("Creating DataFrame and saving results")
            if (self.model_storage > 0):
                #Store all data for the model into a single dataframe and output the result into the path of interest
                # If the reporter was a function with no parameters
                for var, reporter in self.model_reporters.items():
                    if isinstance(reporter, types.LambdaType):
                        self.model_vars[var].append(reporter(self))
                    # Check if function with arguments
                    elif isinstance(reporter, list):
                        self.model_vars[var].append(reporter[0](*reporter[1]))

                #Create the dataFrame and save it to the file location.

            if self.agent_storage > 0:
                # If the reporter was a function with no parameters
                for var, reporter in self.agent_reporters.items():
                    if isinstance(reporter, types.LambdaType):
                        self.agent_vars[var].append(reporter(self))
                    # Check if function with arguments
                    elif isinstance(reporter, list):
                        self.agent_vars[var].append(reporter[0](*reporter[1]))



                #Here we run into an issue where whe have to figure out how to properly return a series of DF's to the batchrunner.
                #So what we can do is overwrite even the ModelReporter code to just work within out current model.
                #This will allow us to send custom df's to the batchrunner to then append onto one final df to save at the end of the program.
                #Try not to save anything here as it wont be concatenated enough to make things work properly.


        self.schedule.step()

        step_time_B = timeit.default_timer()
        self.step_time = step_time_B - step_time_B

        self.stepno = self.stepno + 1
