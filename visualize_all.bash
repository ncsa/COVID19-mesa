#!/bin/bash

# Santiago Nunez-Corrales and Eric Jakobsson
# Illinois Informatics and Molecular and Cell Biology
# University of Illinois at Urbana-Champaign
# {nunezco,jake}@illinois.edu
#
# A simple tunable model for COVID-19 response

# 0. Visualize the population pyramid
python visualize_pop_pyramid.py

# 1. Visualize the Rt callibration
python visualize_rt_with_ci_calib.py outcomes/cu-current-R0-callibration.csv rt_calib.png
python visualize_feature_with_ci_calib.py 0.02 outcomes/cu-current-R0-callibration.csv active_calib.png

# 2. Visualize Rt for all testing levels and counterfactual
python visualize_feature_per_testing.py Rt 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv rt_nisol.png
python visualize_feature_per_testing.py Rt 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv rt_yisol.png

# 3. Visualize active cases for all testing levels and counterfactual
python visualize_feature_per_testing.py SymptQuarantined 80 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv active_nisol.png
python visualize_feature_per_testing.py SymptQuarantined 80 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv active_yisol.png

# 4. Visualize asymptomatic cases for all testing levels and counterfactual
python visualize_feature_per_testing.py Asymptomatic 80 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv asympt_nisol.png
python visualize_feature_per_testing.py Asymptomatic 80 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv asympt_yisol.png

# 5. Visualize severe cases for all testing levels and counterfactual
python visualize_feature_per_testing.py Severe 80 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv severe_nisol.png
python visualize_feature_per_testing.py Severe 80 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv severe_yisol.png

# 6. Visualize private value for all testing levels and counterfactual
python visualize_feature_per_testing.py CumulPrivValue 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv priv_nisol.png
python visualize_feature_per_testing.py CumulPrivValue 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv priv_yisol.png

# 7. Visualize public value for all testing levels and counterfactual
python visualize_feature_per_testing.py CumulPublValue 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv publ_nisol.png
python visualize_feature_per_testing.py CumulPublValue 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv publ_yisol.png
