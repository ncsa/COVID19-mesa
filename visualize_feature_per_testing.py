# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu

# A simple tunable model for COVID-19 response
import matplotlib.pyplot as plt
import scipy.stats as sps
import seaborn as sns
import pandas as pd
import numpy as np
from covidmodel import CovidModel

import sys

feature = sys.argv[1]
in_file__nn = sys.argv[2]
in_file__ny = sys.argv[3]
in_file__yn = sys.argv[4]
in_file__yy = sys.argv[5]
out_file = sys.argv[6]

plt.figure(figsize = (11.7, 8.27))
plt.ticklabel_format(style='plain', axis='y')

df0 = {}

for scn in ["nn", "ny", "yn", "yy"]:
    df0[scn] = pd.read_csv(in_file__nn)
    df0[scn]["Step"] = df0[scn]["Step"]/96

df = {}
xminl = {}
xmaxl = {}
yminl = {}
ymaxl = {}

for scn in ["nn", "ny", "yn", "yy"]:
    df[scn] = pd.DataFrame()
    df[scn]["Step"] = df0[scn]["Step"]
    df[scn][feature] = df0[scn][feature]
    xminl[scn] = df[scn]["Step"].min()
    xmaxl[scn] = df[scn]["Step"].max()
    yminl[scn] = df[scn][feature].min()
    ymaxl[scn] = df[scn][feature].max()

xmin = min(list(xminl.values()))
xmax = max(list(xmaxl.values()))
ymin = min(list(yminl.values()))
ymax = max(list(ymaxl.values()))

avg = {}
low_ci_95 = {}
high_ci_95 = {}
low_ci_99 = {}
high_ci_99 = {}
df_stats = {}

for scn in ["nn", "ny", "yn", "yy"]:
    print(f"Processing case {scn}")
    avg[scn] = [] 
    low_ci_95[scn] = []
    high_ci_95[scn] = []
    low_ci_99[scn] = []
    high_ci_99[scn] = []

    for step in df[scn]["Step"].unique():
        values = df[scn][feature][df[scn]["Step"] == step]
        f_mean = values.mean()
        lci95, hci95 = sps.t.interval(0.95, len(values), loc=f_mean, scale=sps.sem(values))
        lci99, hci99 = sps.t.interval(0.99, len(values), loc=f_mean, scale=sps.sem(values))
        avg[scn].append(f_mean)
        low_ci_95[scn].append(lci95)
        high_ci_95[scn].append(hci95)
        low_ci_99[scn].append(lci99)
        high_ci_99[scn].append(hci99)

    df_stats[scn] = pd.DataFrame()
    df_stats[scn]["Step"] = df[scn]["Step"].unique()
    df_stats[scn]["mean"] = avg[scn]
    df_stats[scn]["lci95"] = low_ci_95[scn]
    df_stats[scn]["hci95"] = high_ci_95[scn]
    df_stats[scn]["lci99"] = low_ci_99[scn]
    df_stats[scn]["hci99"] = high_ci_99[scn]

colpertyp = {}
colpertyp["nn"] = "darkred"
colpertyp["ny"] = "red"
colpertyp["yn"] = "darkblue"
colpertyp["yy"] = "blue"

labpertyp = {}
labpertyp["nn"] = "NT/NI"
labpertyp["ny"] = "NT/WI"
labpertyp["yn"] = "WT/NI"
labpertyp["yy"] = "WT/WI"

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(df_stats["nn"]["Step"], df_stats["nn"]["mean"], color=colpertyp["nn"], linewidth=1, label=labpertyp["nn"])
ax.plot(df_stats["ny"]["Step"], df_stats["ny"]["mean"], color=colpertyp["ny"], linewidth=1, label=labpertyp["ny"])

#plt.legend()

#ax.fill_between(df_stats["Step"], df_stats["lci95"], df_stats["hci95"], color='red', alpha=.1)
#ax.imshow(np.rot90(Z), cmap=plt.cm.binary, extent=[xmin, xmax, ymin, ymax], aspect="auto", interpolation="lanczos")
#plt.xlim([xmin, xmax])
#plt.ylim([ymin, ymax])
#plt.xlabel("Days")
#plt.ylabel("Population fraction")
plt.legend(loc=2)

plt.show()
#plt.savefig(out_file, dpi=300)
