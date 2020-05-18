# COVID19-mesa

*Santiago Nunez-Corrales, Informatics and NCSA, UIUC (nunezco2@illinois.edu)*

*Eric Jakobsson, Molecular and Cell Biology and NCSA, UIUC (jake@illinois.edu)*


A simple simulation to explore contagion by COVID-19 via agent-based modeling (ABM), as well as potential effectiveness of various measures.

**This software is under development rapidly to attempt to respond to the current situation, and should be used bearing this in mind. Any scenarios for specific communities should be considered provisional at all times and revised constantly against the most recent and best curated field evidence.**

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

## Current development needs

- Port to Elixir or any other distributed platform capable of scaling up to 100 km^2 and 100,000 agents

## Acknowledgments

The following individuals have contributed directly and indirectly to rapid development of this software package.

* [Tomas de Camino Beck (ULead)](https://cr.linkedin.com/in/tomas-de-camino-beck-ph-d-a64887102), epidemiology and modeling
* [Tom Pike (Mesa/GMU)](https://github.com/tpike3), Mesa support and Python multiprocessing
* [Rajesh Venkatachalapathy (Portland State University)](https://www.linkedin.com/in/rajesh-venkatachalapathy-8931b1115), agent-based modeling (SPEC)
* [Srikanth Mudigonda (Saint Louis University)](https://www.slu.edu/online/contact-us/faculty/srikanth-mudigonda.php), agent-based modeling (SPEC)
* [Milton Friesen (Cardus, U Waterloo)](https://www.cardus.ca/who-we-are/our-team/mfriesen/), agent-based modeling (SPEC)
* [Jeff Graham (Susquehanna University)](https://www.susqu.edu/academics/faculty/fac/jeffrey-graham), agent-based modeling (SPEC)
* [Galen Arnold (NCSA UIUC)](http://www.ncsa.illinois.edu/assets/php/directory/contact.php?contact=arnoldg), Python optimization strategies 

## Related Literature 

> Incubation time:

* [Lauer, S. A. et al (2020)](https://annals.org/AIM/FULLARTICLE/2762808/INCUBATION-PERIOD-CORONAVIRUS-DISEASE-2019-COVID-19-FROM-PUBLICLY-REPORTED). The incubation period of coronavirus disease 2019 (COVID-19) from publicly reported confirmed cases: estimation and application. Annals of Internal Medicine.

> Probability of severity:

* [Kucharski, A. J. et al. (2020)](https://www.nature.com/articles/s41591-020-0822-7?fbclid=IwAR0tA6W-KvBU3Gy7HqzKGSSZThZM63VgXNCg5vZPKtUmzSWxCUcU71ijAao). Early dynamics of transmission and control of COVID-19: a mathematical modelling study. The Lancet Infectious Diseases.

> Person to person contagion: R_0 of 5.7

* [Sanche, S.et al. (2020)](https://wwwnc.cdc.gov/eid/article/26/7/20-0282_article?deliveryName=USCDC_333-DM25287). "High Contagiousness and Rapid Spread of Severe Acute Respiratory Syndrome Coronavirus 2." Emerging Infectious Diseases 26, no. 7 (2020).
* [Velavan, T. P., & Meyer, C. G. (2020)](https://www.researchgate.net/profile/Thirumalaisamy_Velavan3/publication/339232865_The_Covid-19_epidemic/links/5e4c5bbc92851c7f7f456773/The-Covid-19-epidemic.pdf). The COVID-19 epidemic. Trop Med Int Health, 25(3), 278-280.
* [Wang, Y. et al (2020)](https://onlinelibrary.wiley.com/doi/pdf/10.1002/jmv.25748?casa_token=ED00nZrVSF0AAAAA:gSaam7oJuDOAM1suMJI8AvWJlvgsjuqm5i86hkSfsmlzWkEw5JPbhx4ytO_SrJXHRJJfTHscmFYeQG-C). Unique epidemiological and clinical features of the emerging 2019 novel coronavirus pneumonia (COVID‐19) implicate special control measures. Journal of medical virology.
* [Mizumoto, K., & Chowell, G. (2020)]. Transmission potential of the novel coronavirus (COVID-19) onboard the Diamond Princess Cruises Ship, 2020. Infectious Disease Modelling.
* [Tang, Z., Li, X., & Li, H. (2020)](https://www.medrxiv.org/content/medrxiv/early/2020/03/06/2020.03.03.20030858.full.pdf). Prediction of New Coronavirus Infection Based on a Modified SEIR Model. medRxiv.

> Effectiveness of measures

* [Kraemer, M. U. et al (2020)](https://science.sciencemag.org/content/early/2020/03/25/science.abb4218). The effect of human mobility and control measures on the COVID-19 epidemic in China. Science.
* [Buckee, C. O. et al (2020)](https://science.sciencemag.org/content/early/2020/03/20/science.abb8021). Aggregated mobility data could help fight COVID-19. Science (New York, NY).


> Health system strains
* [Ouyang, H., Argon, N. T., & Ziya, S. (2020)](https://pubsonline.informs.org/doi/pdf/10.1287/opre.2019.1876?casa_token=gCED0n_h3kQAAAAA:xG-KCb4jb2kUpLUwOI5CRq6m1Teq-CYPEX65rhiSaNpHpJPs31y2IyTJnCrvvrfAzJlO0Cy5tK4). Allocation of intensive care unit beds in periods of high demand. Operations Research.

> Agent-based modeling of COVID-19

* [Chang, S. L. et al (2020)](https://arxiv.org/pdf/2003.10218.pdf). Modelling transmission and control of the COVID-19 pandemic in Australia. arXiv preprint arXiv:2003.10218.
* [Biswas, K. et al (2020)](https://arxiv.org/pdf/2003.07063.pdf). Covid-19 spread: Reproduction of data and prediction using a SIR model on Euclidean network. arXiv preprint arXiv:2003.07063.
* [Wang, Q. et al (2020)](https://www.medrxiv.org/content/medrxiv/early/2020/03/27/2020.03.20.20039644.full.pdf). Effectiveness and cost-effectiveness of public health measures to control COVID-19: a modelling study. medRxiv.

> Modeling caveats:
* [Li, J., Blakeley, D., & Smith, R. J. (2011)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3157160/) The failure of 𝑅0. Computational and Mathematical Methods in Medicine.

## Model improvement opportunities

> Considering distance between agents:

* [Fang, Z. et al (2020)](https://arxiv.org/pdf/2002.10616.pdf). How many infections of COVID-19 there will be in the" Diamond Princess"-Predicted by a virus transmission model based on the simulation of crowd flow. arXiv preprint arXiv:2002.10616.


