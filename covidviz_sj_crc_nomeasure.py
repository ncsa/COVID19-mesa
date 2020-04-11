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
df = pd.read_csv("sj_crc_no_measures.csv")
df["Step"] = df["Step"]/96
df_melt = df.melt(id_vars=['Step','Iteration'])
#print(df_melt)
ax = sns.lineplot(x="Step", y="value", hue="variable", data=df_melt, ci=None)
ax.legend(title="SJ/CRC sin medidas", fontsize='small')
ax.set_xlabel("Días")
ax.set_ylabel("Fracción de la población")
plt.savefig("sj_crc_no_measures.png", dpi=300)

