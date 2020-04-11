# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from covidmodel import CovidModel


plt.figure(figsize = (11.7, 8.27))
df = pd.read_csv("cu_il_no_testing.csv")

df0 = pd.DataFrame()
df0["Step"] = df["Step"]/96
df0["Iteration"] = df["Iteration"]
df0["Asymptomatic"] = df["Asymptomatic"]
df0["Symptomatic"] = df["SymptQuarantined"]
df0["Severe"] = df["Severe"]
df0["Cumulative"] = df["Asymptomatic"] + df["SymptQuarantined"] + df["Severe"]


df_melt = df0.melt(id_vars=['Step','Iteration'])
print(df_melt)
#print(df_melt)
ax = sns.lineplot(x="Step", y="value", hue="variable", data=df_melt, ci=None, palette=sns.color_palette('YlOrRd_r', n_colors=4))
ax.legend(title="C-U, Symptomatic", fontsize='small')
ax.set_xlabel("Days")
ax.set_ylabel("Fraction of the population")
#ax.set(yscale="log")
plt.axvline(x=40, linestyle="--", color='black')
plt.savefig("cu_il_callibration.png", dpi=300)

