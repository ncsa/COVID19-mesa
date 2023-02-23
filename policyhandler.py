# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {xinyih8,nunezco,jake}@illinois.edu
from typing import List
from covidpolicy import CovidPolicy

import sys


class PolicyHandler:
    
    def __init__(self, dwell_factor):
        self.policies = []
        self.dwell_factor = dwell_factor
        
    def parse_policy(self, policy_json) -> CovidPolicy:
        # Implement this
        # Also use the duration + start time to compute end time

        is_default = policy_json["is_default"]
        policy_type = policy_json["policy_type"]
        spec = policy_json["spec"] 
        start_time = policy_json["start_time"]
        duration = policy_json["duration"]
        end_time = policy_json["start_time"] + policy_json["duration"]
        self.policies.append(CovidPolicy(
            is_default,
            policy_type,
            spec,
            start_time,
            duration,
            end_time
        ))
        
    
    def parse_all_policies(self, all_policies: List[CovidPolicy]):
        # Implement this
        for p in all_policies:
            self.parse_policy(p)

        self.check_unique_defaults()
        self.check_overlaps()
        
    def add_policy(self, policy: CovidPolicy):
        # Add the policy to the list of policies only when they have not been
        # included before
        
        # Test
        self.policies.append(policy)
        
    def check_overlaps(self):   
        ## TODO: implement this
        
        ## If overlaps exist, call sys.exit(1)
        # Policies of different type are ok. Only 
        for p in self.policies:
            for m in self.policies:
                if p.policy_type == m.policy_type:
                    if p.start_time > m.start_time and p.start_time < m.end_time:
                        sys.exit(1)
    
    def check_unique_defaults(self):
        # Implement this
        for p in self.policies:
            for m in self.policies:
                if p.policy_type == m.policy_type:
                    if p.is_default == True and m.is_default == True:
                        print("error: Two defaults")
    
    def filter_unique_defaults(self):
        # Select only those that are defaults after veryfing they are unique
        # Implement this filter using the property `is_default` from CovidPolicy
        # This happen during initialization self.check_unique_defaults()

        unique_defaults = []
        for p in self.policies:
            if p.is_default == True:
                unique_defaults.append(p)

        return unique_defaults # Replace by a list comprehension
        # Python higher order functions
    
    def filter_by_start_time(self, time):
        # Implement the filter
        # Observations:
        #
        # 1. Current time IS different from the step number
        # 2. CovidPolicy objects -> the property start_time is an attribute
        # 3. List comprehensions -> use it
        start = []
        for p in self.policies:
            if p.start_time == time:
                start.append(p)

        return start     
    
    def filter_by_end_time(self, time):
        # Implement the filter
        end = []
        for p in self.policies:
            if p.end_time == time:
                end.append(p)

        return end

    def set_default(self, model_dataclass):
        # Implement this
        #
        # 1. Filter unique defaults
        # 2. Apply all defaults
        
        defaults = self.filter_unique_defaults()
        
        for p in defaults:
            self.apply_policy_measure(p, model_dataclass)
    
    def apply_policy_measure(self, policy: CovidPolicy, model_dataclass):
        policy_functions = {
            "isolation": self.apply_isolation,
            "tracing": self.apply_contact_tracing,
            "distancing": self.apply_social_and_masks,
            "vaccination": self.apply_vaccination
        }
        
        policy_functions[policy.policy_type](policy, model_dataclass)
    
    def apply_isolation(self, policy, model_dataclass):
        # TODO: remember that all policy measures have a start time and a duration
        model_dataclass.isolation_rate = policy.spec["isolation_rate"]
        model_dataclass.prob_isolation_effective = policy.spec["prob_isolation_effective"]
        model_dataclass.start_time = policy.spec["start_time"]
        model_dataclass.duration = policy.spec["duration"]
        model_dataclass.end_time = policy.spec["start_time"] + policy.spec["duration"]
    
    def apply_vaccination(self, policy, model_dataclass):
        # TODO: remember that all policy measures have a start time and a duration
        model_dataclass.vaccination_chance = policy.spec["vaccination_chance"]
        model_dataclass.vaccine_cost = policy.spec["vaccine_cost"]
        model_dataclass.vaccine_count = policy.spec["vaccine_count"]
        model_dataclass.vaccinated_count = policy.spec["vaccinated_count"]
        model_dataclass.vaccinated_percent = policy.spec["vaccinated_percent"]
        # add parameters
        model_dataclass.effective_period = policy.spec["effective_period"]
        model_dataclass.effectiveness = policy.spec["effectiveness"]
        model_dataclass.now = True

        model_dataclass.start_time = policy.spec["start_time"]
        model_dataclass.duration = policy.spec["duration"]
        model_dataclass.end_time = policy.spec["start_time"] + policy.spec["duration"]
        # TODO: check against model_data attributes pertaining to vaccination, some missing ones        

    def apply_social_and_masks(self, policy, model_dataclass):
        # TODO: remember that all policy measures have a start time and an end time
        model_dataclass.testing_rate = policy.spec["testing_rate"] 
        model_dataclass.distancing = policy.spec["distancing"] 
        model_dataclass.start_time = policy.spec["start_time"]
        model_dataclass.duration = policy.spec["duration"]
        model_dataclass.end_time = policy.spec["start_time"] + policy.spec["duration"]
    
    def apply_contact_tracing(self, policy, model_dataclass):
        # Set the start and end time using a start spec and a duration
        model_dataclass.tracing_start = policy.spec["tracing_start"]
        model_dataclass.tracing_end = model_dataclass.tracing_start + policy.spec["days_tracing_lasts"]*self.dwell_factor
        model_dataclass.tracing_now = True
        model_dataclass.start_time = policy.spec["start_time"]
        model_dataclass.duration = policy.spec["duration"]
        model_dataclass.end_time = policy.spec["start_time"] + policy.spec["duration"]
    
    def dispatch(self, model_dataclass, time):
        # Obtain all policies that start at this moment and apply them
        start_now = self.filter_by_start_time(time)
        
        for p in start_now:
            self.apply_policy_measure(p, model_dataclass)

    def reverse_dispatch(self, model_dataclass, time):
        # Obtain all policies that start at this moment and apply them
        start_now = self.filter_by_end_time()
        
        for p in start_now:
            self.apply_policy_measure(p, model_dataclass)

        