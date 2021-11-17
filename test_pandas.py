import pandas as pd
import numpy as np
df = pd.DataFrame()


random_data =["Tom", "Hank", "Laurel", "Yanny", "Daniel"]
data_list = []
agent_data_column_name_list = []
for index, agent in enumerate(model.schedule_agents): #Creates a column for each agent and parameter
    for param_name in parameter_names: #Retrieves the name of the parameters for that particular agent and adds it to the list of column headings. parameter_names will be a list of strings
        agent_data_column_name_list.append("Agent "+ str(index) +" " + param_name)


"""agent data after every step will come in the form of a variable list if possible?"""
#We  have to store the parameter names as a list. Then we will have to retrieve the variable with that name and place it onto the list in the order defined by the head list.
#how do you access an agent's data with a list that is based on the variable names? Is it a direct reference to the variable?

"""Tuple?"""
# extracts tuple
# Extracts the list of tuples then take the data we want?
# Extracts only the data that we want.
# We can do the method like the model data collection
# We pass by a variable and a function
# Or we actual;ly pass in agent variables along with functions retrieving the variables
for i in inspect.getmembers(agent):
    # to remove private and protected
    # functions
    if not i[0].startswith('_'):
        # To remove other methods that
        # doesnot start with a underscore
        if not inspect.ismethod(i[1]):
            (x, y) = i
            if (agent_data_column_name_list.find(x)):



print(data)

for index, name in enumerate(random_data):
    data = []
    data.append(name)
    data.append(index * index)
    data_list.append(data)

print (data_list)
df = pd.DataFrame(data_list , columns =data_column_list)
print(df)
df.to_csv("test_pandas.csv")