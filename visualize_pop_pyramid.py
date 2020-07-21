# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu
#
# A simple tunable model for COVID-19 response
import pandas as pd
import matplotlib.pyplot as plt

plt.figure(figsize = (11.7, 8.27))
plt.ticklabel_format(style='plain', axis='y')

# Read data
df = pd.read_csv("cu-pop-data.csv")

a = plt.barh(df["Age"], df["Population Fraction"], color = 'darkblue')
b = plt.barh(df["Age"], -df["Mortality"], color = 'darkred')

for i, v in enumerate(df["Population Fraction"]):
    plt.text(v + 0.5, i, str(v), color='darkblue')

for i, v in enumerate(df["Mortality"]):
    plt.text(-v - 3.6, i, str(v), color='darkred')

# Decorations
plt.tick_params(
    axis='x',
    which='both',
    bottom=False,
    top=False,        
    labelbottom=False)    
plt.xlabel("Percentage")
plt.ylabel("Age group")
plt.legend((a[0], b[0]), ("Population Fraction", "Mortality"))
plt.savefig("cu_demographics.png", dpi=300)
