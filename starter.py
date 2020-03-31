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

