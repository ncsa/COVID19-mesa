#!/bin/bash

# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu
#
# A simple tunable model for COVID-19 response

# 1. Visualize active cases for business closure models
python visualize_feature_per_closings.py SymptQuarantined 80.0 0.04 0.0 outcomes/cu-50-nisol-bars.csv.csv outcomes/cu-50-nisol-rest.csv.csv outcomes/cu-50-nisol-phs3.csv.csv outcomes/cu-50-nisol.csv.csv active_phase_3.png

# 1. Visualize severe cases for business closure models
python visualize_feature_per_closings.py Severe 80 0.0004 0.0 outcomes/cu-50-nisol-bars.csv.csv outcomes/cu-50-nisol-rest.csv.csv outcomes/cu-50-nisol-phs3.csv.csv outcomes/cu-50-nisol.csv.csv severe_phase_3.png
