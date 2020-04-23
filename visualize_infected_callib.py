# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from covidmodel import CovidModel

import sys

in_file = sys.argv[1]
out_file = sys.argv[2]

plt.figure(figsize = (11.7, 8.27))
plt.ticklabel_format(style='plain', axis='y')
df0 = pd.read_csv(in_file)
df0["Step"] = df0["Step"]/96
df = df0[["Step", "Iteration", "Exposed", "SymptQuarantined"]]
df_melt = df.melt(id_vars=['Step','Iteration'])
axv = sns.lineplot(x="Step", y="value", hue="variable", data=df_melt, ci=None)
axv.legend(title="Model", fontsize='small')
axv.set_xlabel("Days")
axv.set_ylabel("Infected")
plt.axhline(y=0, linestyle="--", color='black')
plt.savefig(out_file, dpi=300)


