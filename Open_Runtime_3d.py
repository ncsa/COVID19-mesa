import pickle
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d.axes3d import Axes3D
import matplotlib.patches as mpatches


agent_count_list = [100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000] #X-Coordinate
print(agent_count_list)
print(agent_count_list[0:10])
print(agent_count_list[10:21])

iteration_list = [1,2,3,4] #Y-Coordinate

# agent_count_list = [100,200,300,400,500,600,700,800,900,1000,1100,1200] #X-Coordinate
# iteration_list = [1,2,3,4,5,6,7,8,9,10,11,12] #Y-Coordinate

# """Backtracking Files"""
# data_storage_file_1 = "outcomes/Debugging/Test_Runtime/Data_Storage_Times.csv"
# backtracking_df_1 = pd.read_csv(data_storage_file_1)
# data_storage_file_2 = "outcomes/Debugging/Test_Runtime/Data_Storage_Times.csv"
# backtracking_df_2 = pd.read_csv(data_storage_file_2)
# frames = [backtracking_df_1, backtracking_df_2]
# backtracking_data_storage_df = pd.concat(frames)


"""No Backtracking Files"""
No_backtracking_data_storage_file_1 = "outcomes/Debugging/Test_Runtime/Total_Running_Times_0_10_No_backtracking.csv"
No_backtracking_df_1 = pd.read_csv(No_backtracking_data_storage_file_1)
data_storage_file_2 = "outcomes/Debugging/Test_Runtime/Total_Running_Times_10_21_No_backtracking.csv"
backtracking_df_2 = pd.read_csv(data_storage_file_2)
frames = [No_backtracking_df_1, backtracking_df_2]
no_backtracking_data_storage_df = pd.concat(frames, ignore_index = True)

""""Backtracking Files"""
backtracking_data_storage_file_1 = "outcomes/Debugging/Test_Runtime/Total_Running_Times_0_10_backtracking.csv"
backtracking_df_1 = pd.read_csv(backtracking_data_storage_file_1)
# data_storage_file_2 = "outcomes/Debugging/Test_Runtime/Data_Storage_Times.csv"
# backtracking_df_2 = pd.read_csv(data_storage_file_2)
nb_frames = [backtracking_df_1]
backtracking_data_storage_df = pd.concat(nb_frames, ignore_index = True)



No_Backtracking_Data_Storage_Times = []
print(no_backtracking_data_storage_df)
for index in range(len(np.array(no_backtracking_data_storage_df))):
    for iteration in iteration_list:
        time = no_backtracking_data_storage_df["Iteration"+str(iteration)][index]
        No_Backtracking_Data_Storage_Times.append(time)

Backtracking_Data_Storage_Times = []
print(backtracking_data_storage_df)
for index in range(len(np.array(backtracking_data_storage_df))):
    for iteration in iteration_list:
        time = backtracking_data_storage_df["Iteration"+str(iteration)][index]
        Backtracking_Data_Storage_Times.append(time)


fig = plot.figure()
ax = fig.add_subplot(111, projection='3d')

x, y = np.meshgrid(iteration_list,agent_count_list[0:len(no_backtracking_data_storage_df)])
print(x)
print(y)
print(np.array(No_Backtracking_Data_Storage_Times).reshape(x.shape))
ax.plot_surface(x, y, np.array(No_Backtracking_Data_Storage_Times).reshape(x.shape), color="blue", label="No_Backtracking", linewidth=1)
# ax2.plot_surface(x, y, np.array(Backtracking_Data_Storage_Times).reshape(x.shape), color="red", label="Backtracking", linewidth=1)

plot.show()
legends_list = []
legend1 = mpatches.Patch(color="red")
legends_list.append(legend1)
legend2 = mpatches.Patch(color="blue")
legends_list.append(legend2)
plot.axis('tight')
names = ["Backtracking", "No_Backtracking"]
plot.legend(legends_list, names, bbox_to_anchor=(1.05, 0.8), loc="upper right", borderaxespad=0,fontsize='xx-small')
ax.set_title("Data Storage Times")
ax.set_xlabel("Iteration Count")
ax.set_ylabel("Agent Count")
ax.set_zlabel("Storage Time")
plot.show()
out_file = "visualizations/Debugging/Test_Runtime/Data_Storage_Time"
pickle.dump(fig, open(out_file+".fig.pickle", 'wb')) # This is for Python 3 - py2 may need `file` instead of `open`
plot.close()