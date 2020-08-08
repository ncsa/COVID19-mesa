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
from scipy.ndimage import gaussian_filter1d
from covidmodel import CovidModel

import sys

feature = sys.argv[1]
start = float(sys.argv[2])
top = float(sys.argv[3])
bottom = float(sys.argv[4])
in_file = {}
in_file["25"] = sys.argv[5]
in_file["50"] = sys.argv[6]
in_file["75"] = sys.argv[7]
in_file["cf"] = sys.argv[8]
out_file = sys.argv[9]

cases = ["25", "50", "75", "cf"]

plt.figure(figsize = (11.7, 8.27))
plt.ticklabel_format(style='plain', axis='y')

df0 = {}

for scn in cases:
    df0[scn] = pd.read_csv(in_file[scn])
    df0[scn]["Step"] = df0[scn]["Step"]/96

df = {}
# Used when there is
df_temp = {}
xmaxl = {}

for scn in cases:
    df[scn] = pd.DataFrame()

    if feature == "Rt":
        for iteration in df0[scn]["Iteration"].unique():
            df_temp[scn] = pd.DataFrame()
            df_temp[scn]["Step"] = (df0[scn]["Step"].unique())
            df_temp[scn]["Rt"] = gaussian_filter1d(df0[scn]["Rt"][df0[scn]["Iteration"] == iteration], 96)
            df[scn] = df[scn].append(df_temp[scn])

    else:
        df[scn]["Step"] = df0[scn]["Step"]
        df[scn][feature] = df0[scn][feature]

    xmaxl[scn] = df[scn]["Step"].max()

#xmin = min(list(xminl.values()))
xmin = start
xmax = max(list(xmaxl.values()))
ymin = bottom
ymax = top

avg = {}
low_ci_95 = {}
high_ci_95 = {}
low_ci_99 = {}
high_ci_99 = {}
df_stats = {}

for scn in cases:
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

colpertyp["25"] = "darkred"
colpertyp["50"] = "teal"
colpertyp["75"] = "darkblue"
colpertyp["cf"] = "purple"

labpertyp = {}
labpertyp["25"] = "25%"
labpertyp["50"] = "50%"
labpertyp["75"] = "75%"
labpertyp["cf"] = "CF"

for scn in cases:
    plt.plot(df_stats[scn]["Step"], df_stats[scn]["mean"], color=colpertyp[scn], linewidth=1, label=labpertyp[scn])
    plt.fill_between(df_stats[scn]["Step"], df_stats[scn]["lci95"], df_stats[scn]["hci95"], color=colpertyp[scn], alpha=.1)

plt.vlines(116, 0, ymax, colors='gray', linestyle=":")
plt.vlines(130, 0, ymax, colors='gray', linestyle="-.")
plt.vlines(136, 0, ymax, colors='gray', linestyle="--")

plt.xlim([xmin, xmax])
plt.ylim([ymin, ymax])
plt.xlabel("Days since April 15, 2020", fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.legend(fontsize=16, title="Scenario", title_fontsize=18)

if (feature == "SymptQuarantined") or (feature == "Asymptomatic") or (feature == "Severe"):
    plt.ylabel("Population Fraction", fontsize=18)
elif feature == "CumulPublValue":
    plt.ylabel("Public Value", fontsize=18)
elif feature == "CumulPrivValue":
    plt.ylabel("Private Value", fontsize=18)
elif feature == "Rt":
    plt.ylabel("$R(T)$", fontsize=18)
else:
    plt.ylabel("variable", fontsize=18)

plt.savefig(out_file, dpi=300)
