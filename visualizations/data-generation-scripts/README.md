## Generating per agent per step data

Spin up the COVID-mesa server following the instruction of the project README file. For example, run
```bash
python3 covidserver.py scenarios/cu-counterfactual-with-variant.json 
```

Open `pull_data.ipynb` under the project Python `.venv` environment and run all the cells to generate a collector for agent data and put the output files under `/dashboard-server/data` to view them in the dashboard. See the README under `/dashboard-server`.