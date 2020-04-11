#!/bin/bash

# Run the callibration first
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_callibration.py

# Run the trend visualizations per testing level
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_no_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_05pc_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_10pc_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_20pc_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_40pc_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_50pc_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_75pc_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_90pc_testing.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_all_testing.py

# Run the summary statistics
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_symptomatic.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_asymptomatic.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_severe.py
/home/snunez/Development/COVID19-mesa/.venv/bin/python3 /home/snunez/Development/COVID19-mesa/covidviz_cu_il_deaths.py

