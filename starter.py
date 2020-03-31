# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
from covidmodel import CovidModel
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

cm = CovidModel(50, 10, 10, False)

for i in range(100):
    cm.step()

#trends = cm.datacollector.get_model_vars_dataframe()
#print(trends)

#positions = cm.datacollector.get_agent_vars_dataframe()
#print(positions)

#positions.to_csv('agent_pos.csv')

