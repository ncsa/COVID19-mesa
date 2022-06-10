# COVID19-mesa


## Authors 

*Santiago Nunez-Corrales, Informatics and NCSA, UIUC (nunezco2@illinois.edu)*

*Eric Jakobsson, Molecular and Cell Biology and NCSA, UIUC (jake@illinois.edu)*

## Developers 

* Angelo Santos
* Boda Song
* Xinyi Huang


A simple simulation to explore contagion by COVID-19 via agent-based modeling (ABM), as well as potential effectiveness of various measures.

**This software is under development rapidly to attempt to respond to the current situation, and should be used bearing this in mind. Any scenarios for specific communities should be considered provisional at all times and revised constantly against the most recent and best curated field evidence.**

Reference publication: 

*Núñez-Corrales, S., & Jakobsson, E. (2020). The Epidemiology Workbench: a Tool for Communities to Strategize in Response to COVID-19 and other Infectious Diseases. [medRxiv](https://www.medrxiv.org/content/10.1101/2020.07.22.20159798v2).*

## Installation (Linux and friends)

1. Clone the repository:

```bash
git clone https://github.com/snunezcr/COVID19-mesa.git
```

2. Create, and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Update pip

```bash
pip install --upgrade pip
```
4. Install dependencies

```bash
pip install -r requirements.txt
```

## Execution

The following requires activating the Python virtual environment of your COVID19-mesa install if it is not previously active:

```bash
source .venv/bin/activate
```

To execute the dashboard interface:

```bash
(.venv) python covidserver.py
```

To execute a scenario stored in `scenarios/`:

```bash
(.venv) python model_runner.py [processors] scenarios/[filename]
```

After execution, a CSV file will be stored.

## Model features

* JSON configurable
* Single-run visual dashboard for a selection of variables of interest
* Batch execution of models with graphic reporting and multiprocessing
* Models
  * Demographic (age/sex distribution/mortality)
  * Epidemiological (extension of SEIR), including R(t)
  * Policy measures including
    * Shelter at home
    * Social distancing based on latest findings (8-feet aerosol spread)
    * Testing based on random resampling of not-infected parts of the population
    * Testing based on contact tracing
  * Simple micro/macro input-output matrix economic response *[experimental]*
  * Simple pandemic-driven unemployment trends

## Model callibration protocol

Model callibration requires the best possible clinical data estimates for two parameters: the average incubation time and proportion of asyomptomatic patients:

* For the average incubation time, hospital triaging of COVID-19 cases can provide information leading to estimates. Incubation time is likely to be blurred by multiple confusion variables captured in our model as a Poisson distribution. Despite its stochasticity, the model supposes that large population sizes group tightly towards a mean value. This assumption may need to be revised retrospectively later.
* For the proportion of asymptomatics, contact tracing and structured testing can provide specific local information.

### Suggested callibration steps

1. Adjust grid size based on fixed population density until R0 matches the best known value for the area in the first days of the model (steps = 96) and > 30 runs. Population density in the model loosely includes average mobility patterns, and cell sizes reflect the distance traversed every 15 minutes. Also -but not recommended- the probability of contagion may be used to callibrate. This may imply unknown population conditions and should be used only to test hypotheses about individual variations that manifest in the ability of COVID-19 to spread.
2. Execute the model to the point where the number of symptomatic agents corresponds to one representative agent. For example, with an ABM of 1000 agents and a population of 100k individuals, the critical infected agent-to-population ratio is 1:100. Use the point in time rounded to the nearest integer day as point of departure for policy measures. In practice, this implies executing the model in excess of three days the incubation period.
3. If policy measures have been introduced mandatorily, use date above as the reference point for their introduction.

### Scenario creation

To develop scenarios, we strongly recommend starting from the most recently callibrated model that includes policies as well as usin a model without measures as a basis for counterfactual arguments.

## Acknowledgments

The following individuals have contributed directly and indirectly to rapid development of this software package.

* [Tomas de Camino Beck (ULead)](https://cr.linkedin.com/in/tomas-de-camino-beck-ph-d-a64887102), epidemiology and modeling
* [Tom Pike (Mesa/GMU)](https://github.com/tpike3), Mesa support and Python multiprocessing
* [Mark Isken (MIS/Oakland State University)](http://www.sba.oakland.edu/faculty/isken/), Model development, testing and application
* [Rajesh Venkatachalapathy (Portland State University)](https://www.linkedin.com/in/rajesh-venkatachalapathy-8931b1115), agent-based modeling (SPEC)
* [Srikanth Mudigonda (Saint Louis University)](https://www.slu.edu/online/contact-us/faculty/srikanth-mudigonda.php), agent-based modeling (SPEC)
* [Milton Friesen (Cardus, U Waterloo)](https://www.cardus.ca/who-we-are/our-team/mfriesen/), agent-based modeling (SPEC)
* [Jeff Graham (Susquehanna University)](https://www.susqu.edu/academics/faculty/fac/jeffrey-graham), agent-based modeling (SPEC)
* [Galen Arnold (NCSA UIUC)](http://www.ncsa.illinois.edu/assets/php/directory/contact.php?contact=arnoldg), Python optimization strategies 




