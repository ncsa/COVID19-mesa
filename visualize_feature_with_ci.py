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
ymax = float(sys.argv[2])
label = sys.argv[3]
in_file = sys.argv[4]
out_file = sys.argv[5]

plt.figure(figsize = (11.7, 8.27))
plt.ticklabel_format(style='plain', axis='y')
df0 = pd.read_csv(in_file)
df0["Step"] = df0["Step"]/96

df = pd.DataFrame()
df["Step"] = df0["Step"]
df[feature] = df0[feature]#*100

xmin = 0
xmax = df["Step"].max()
ymin = df[feature].min()

avg = []
low_ci_95 = []
high_ci_95 = []
low_ci_99 = []
high_ci_99 = []

print(f"Computing confidence intervals...")

for step in df["Step"].unique():
    values = df[feature][df["Step"] == step]
    f_mean = values.mean()
    lci95, hci95 = sps.t.interval(0.95, len(values), loc=f_mean, scale=sps.sem(values))
    lci99, hci99 = sps.t.interval(0.99, len(values), loc=f_mean, scale=sps.sem(values))
    avg.append(f_mean)
    low_ci_95.append(lci95)
    high_ci_95.append(hci95)
    low_ci_99.append(lci99)
    high_ci_99.append(hci99)

df_stats = pd.DataFrame()
df_stats["Step"] = df["Step"].unique()
df_stats["mean"] = avg
df_stats["lci95"] = low_ci_95
df_stats["hci95"] = high_ci_95
df_stats["lci99"] = low_ci_99
df_stats["hci99"] = high_ci_99

fig, ax = plt.subplots()
ax.plot(df_stats["Step"], df_stats["mean"], color="red")
ax.fill_between(df_stats["Step"], df_stats["lci95"], df_stats["hci95"], color='orangered', alpha=.1)
ax.vlines(116, 0, ymax, colors='gray', linestyle=":")
ax.vlines(130, 0, ymax, colors='gray', linestyle="-.")
ax.vlines(136, 0, ymax, colors='gray', linestyle="--")
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])
ax.set_xlabel("Days")
ax.set_ylabel("Pop. Fraction")
plt.savefig(out_file, dpi=300)
