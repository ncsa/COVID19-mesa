# COVID19-mesa

*Santiago Nunez-Corrales, Informatics and NCSA, UIUC (nunezco2@illinois.edu)*
*Eric Jakobsson, Molecular and Cell Bioogy and NCSA, UIUC (jake@illinois.edu)*


A simple simulation to explore contagion by COVID-19 via agent-based modeling (ABM), as well as potential effectiveness of various measures.

**This software is under development rapidly to attempt to respond to the current situation, and should be used bearing this in mind.**


## Current development needs

- Port to Elixir or any other distributed platform capable of scaling up to 100 km^2 and 100,000 agents
- Integration of econometric models to evaluate community recovery and response
- 

## Acknowledgments

* Tomas de Camino Beck, epidemiologist and modeling
* Rajesh Venkatachalapathy, agent-based modeling

## Related Literature 

> Incubation time:

* [Lauer, S. A. et al (2020)](https://annals.org/AIM/FULLARTICLE/2762808/INCUBATION-PERIOD-CORONAVIRUS-DISEASE-2019-COVID-19-FROM-PUBLICLY-REPORTED). The incubation period of coronavirus disease 2019 (COVID-19) from publicly reported confirmed cases: estimation and application. Annals of Internal Medicine.

> Probability of severity:

* [Kucharski, A. J. et al. (2020)](https://www.nature.com/articles/s41591-020-0822-7?fbclid=IwAR0tA6W-KvBU3Gy7HqzKGSSZThZM63VgXNCg5vZPKtUmzSWxCUcU71ijAao). Early dynamics of transmission and control of COVID-19: a mathematical modelling study. The Lancet Infectious Diseases.

> Person to person contagion: R_0 of 3.58

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


