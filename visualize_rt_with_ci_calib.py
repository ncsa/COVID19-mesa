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
import sys

from scipy.ndimage import gaussian_filter1d
from covidmodel import CovidModel

in_file = sys.argv[1]
out_file = sys.argv[2]

plt.figure(figsize = (11.7, 8.27))
plt.ticklabel_format(style='plain', axis='y')
df0 = pd.read_csv(in_file)

# Rt is trickier. We need to soften each run by applying a Gaussial kernel
print(f"Softening RT values...")

df = pd.DataFrame()

for iteration in df0["Iteration"].unique():
    df_temp = pd.DataFrame()
    df_temp["Step"] = (df0["Step"].unique())/96
    df_temp["Rt"] = gaussian_filter1d(df0["Rt"][df0["Iteration"] == iteration], 96)
    df = df.append(df_temp)

xmin = 0
xmax = df["Step"].max()
ymin = 0
ymax = df["Rt"].max()

avg = []
low_ci_95 = []
high_ci_95 = []
low_ci_99 = []
high_ci_99 = []

print(f"Computing confidence intervals...")

for step in df["Step"].unique():
    values = df["Rt"][df["Step"] == step]
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
ax.fill_between(df_stats["Step"], df_stats["lci95"], df_stats["hci95"], color='red', alpha=.1)
ax.set_xlim([xmin, xmax])
ax.set_ylim([xmin, ymax])
ax.set_xlabel("Days")
ax.set_ylabel("R(t)")
ax.set_title("Effective reproductive number")
ax.hlines(1.71, xmin, xmax, colors='g', linestyles='--')
ax.hlines(1.20, xmin, xmax, colors='g', linestyles='--')
ax.legend()
plt.savefig(out_file, dpi=300)
