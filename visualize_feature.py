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
in_file = sys.argv[5]
out_file = sys.argv[6]

df0 = pd.read_csv(in_file)
df0["Step"] = df0["Step"]/96

# Used when there is
xmaxl = {}


df = pd.DataFrame()

if feature == "Rt":
    for iteration in df0["Iteration"].unique():
        df_temp = pd.DataFrame()
        df_temp["Step"] = (df0["Step"].unique())
        df_temp["Rt"] = gaussian_filter1d(df0["Rt"][df0["Iteration"] == iteration], 96)
        df = df.append(df_temp)
else:
    df["Step"] = df0["Step"]
    df[feature] = df0[feature]

#xmin = min(list(xminl.values()))
xmin = start
xmax = df["Step"].max()
ymin = bottom
ymax = top

avg = {}
low_ci_95 = {}
high_ci_95 = {}
low_ci_99 = {}
high_ci_99 = {}
df_stats = {}

avg = [] 
low_ci_95 = []
high_ci_95 = []
low_ci_99 = []
high_ci_99 = []

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

plt.plot(df_stats["Step"], df_stats["mean"], color='black', linewidth=1)
plt.fill_between(df_stats["Step"], df_stats["lci95"], df_stats["hci95"], color='blue', alpha=.1)

plt.xlim([xmin, xmax])
plt.ylim([ymin, ymax])
plt.xlabel("Days since April 15, 2020", fontsize=18)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

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
