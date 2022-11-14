# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {xinyih8,nunezco,jake}@illinois.edu
from typing import List
from covidpolicy import CovidPolicy

import sys


class PolicyHandler:
    
    def __init__(self):
        self.policies = []  
        
    def parse_policy(self, policy_json) -> CovidPolicy:
        # Implement this
        # Also use the duration + start time to compute end time
        pass
    
    def parse_all_policies(self, all_policies: List[CovidPolicy]):
        # Implement this
        pass
        
    def add_policy(self, policy: CovidPolicy):
        # Add the policy to the list of policies only when they have not been
        # included before
        
        # Test
        self.policies.append(policy)
        
    def check_overlaps(self):
        ## TODO: implement this
        
        ## If overlaps exist, call sys.exit(1)
        pass
    
    def check_unique_defaults(self):
        # Implement this
        pass
    
    def filter_unique_defaults(self):
        # Select only those that are defaults after veryfing they are unique
        # Implement this filter using the property `is_default` from CovidPolicy
        return self.policies
    
    def filter_by_start_time(self):
        # Implement the filter
        return self.policies
    
    def filter_by_end_time(self):
        # Implement the filter
        return self.policies

    def set_default(self, model):
        # Implement this
        #
        # 1. Filter unique defaults
        # 2. Apply all defaults
        
        defaults = self.filter_unique_defaults()
        
        for p in defaults:
            self.apply_policy_measure(p, model)
    
    def apply_policy_measure(self, policy: CovidPolicy, model):
        policy_functions = {
            "isolation": self.apply_isolation,
            "tracing": self.apply_contact_tracing,
            "distancing": self.apply_social_and_masks,
            "vaccination": self.apply_vaccination
        }
        
        policy_functions[policy.policy_type](policy, model)
    
    def apply_isolation(self, policy, model):
        # Implement
        pass
    
    def apply_vaccination(self, policy, model):
        # Implement
        pass
    
    def apply_social_and_masks(self, policy, model):
        # Implement
        pass
    
    def apply_contact_tracing(self, policy, model):
        # Implement
        pass
    
    def dispatch(self, model):
        # Obtain all policies that start at this moment and apply them
        start_now = self.filter_by_start_time()
        
        for p in start_now:
            self.apply_policy_measure(p, model)
        