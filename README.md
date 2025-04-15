#### Replication package for the paper:

*On the Role of Search Budgets in Model-Based Software Refactoring Optimization*\
by J. Andres Diaz-Pace, Daniele Di Pompeo, and Michele Tucci

#### How to generate the tables and figures in the paper
Initialize the python execution environment:
```bash
git clone https://github.com/SpencerLabAQ/replication_package_search-budget.git
cd replication-package_search-budget
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Generate tables and figures:
```bash
python HV_table_and_timeline.py
python time_and_algo_comparison.py
python superpareto_scatter.py
```

#### Experiments

The experiments in the paper were performed using [EASIER](http://sealabtools.di.univaq.it/EASIER/), which is available in a different repository:

[https://github.com/SEALABQualityGroup/EASIER](https://github.com/SEALABQualityGroup/EASIER)

The data gathered during such experiments is provided here, in the [data](data) folder.
