# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {xinyih8,nunezco,jake}@illinois.edu
from dataclasses import dataclass


@dataclass
class CovidPolicy:
    is_default: bool
    policy_type: str
    spec: dict()
    start_time: int
    duration: int
    end_time: int
