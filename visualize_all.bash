#~/bin/bash

# 1. Visualize the Rt callibration
python visualize_rt_with_ci_calib.py outcomes/cu-current-R0-callibration.csv rt_calib.png

# 2. Visualize Rt for all testing levels and counterfactual
python visualize_feature_per_testing.py Rt 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv rt_nisol.png
python visualize_feature_per_testing.py Rt 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv rt_yisol.png

# 3. Visualize active cases for all testing levels and counterfactual
python visualize_feature_per_testing.py SymptQuarantined 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv active_nisol.png
python visualize_feature_per_testing.py SymptQuarantined 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv active_yisol.png

# 4. Visualize asymptomatic cases for all testing levels and counterfactual
python visualize_feature_per_testing.py Asymptomatic 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv asympt_nisol.png
python visualize_feature_per_testing.py Asymptomatic 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv asympt_yisol.png

# 5. Visualize severe cases for all testing levels and counterfactual
python visualize_feature_per_testing.py Severe 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv severe_nisol.png
python visualize_feature_per_testing.py Severe 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv severe_yisol.png

# 6. Visualize private value for all testing levels and counterfactual
python visualize_feature_per_testing.py CumulPrivValue 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv priv_nisol.png
python visualize_feature_per_testing.py CumulPrivValue 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv priv_yisol.png

# 7. Visualize public value for all testing levels and counterfactual
python visualize_feature_per_testing.py CumulPublValue 0 outcomes/cu-25-nisol.csv.csv outcomes/cu-50-nisol.csv.csv outcomes/cu-75-nisol.csv.csv oucomes/cu-counterfactual.csv.csv publ_nisol.png
python visualize_feature_per_testing.py CumulPublValue 0 outcomes/cu-25-yisol.csv.csv outcomes/cu-50-yisol.csv.csv outcomes/cu-75-yisol.csv.csv oucomes/cu-counterfactual.csv.csv publ_yisol.png