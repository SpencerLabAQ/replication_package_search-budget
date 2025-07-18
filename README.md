# Replication package for the paper:

*On the Role of Search Budgets in Model-Based Software Refactoring Optimization*\
by J. Andres Diaz-Pace, Daniele Di Pompeo, and Michele Tucci

## How to generate the tables and figures in the paper
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

---

## Experiments

### Running the Genetic Algorithm Docker Image

This guide outlines the deployment and execution process of our genetic algorithm framework using Docker. The framework is encapsulated within a Docker image, hosted on Docker Hub, for easy execution with minimal setup required.

#### Prerequisites

- Docker installed on your system.
- Internet connection for downloading the Docker image and necessary artifacts.

#### Setup and Execution

##### Step 1: Pulling the Docker Image

First, ensure that Docker is running on your system. Then, pull the Docker image using the following command:

```bash
docker pull danieledipompeo/easier:v1.1
```

##### Step 2: Running the Container

Run the container with the following command, ensuring to replace `<host_folder>` with your specific path for output data:

```bash
docker run -d --log-driver=journald \
--rm --mount type=tmpfs,destination=/tmp \
-v <host_folder>:/mnt/easier-output/ \
danieledipompeo/easier:v1.1 \
<configuration_file>
```

###### Command Details

- `-d` runs the container in detached mode.
- `--log-driver=journald` configures logging to use the journald driver.
- `--rm` removes the container after it exits.
- `--mount` and `-v` options are used for managing temporary files and output data respectively.
- `<configuration_file_url>` the URL specifies the configuration file, which is downloaded automatically (e.g., https://github.com/danieledipompeo/easier-experiment-data/tree/main/nsgaii-ttbs-energy).

### Compatibility

The framework has been tested on Debian, but should be compatible with other Linux distributions or operating systems that support Docker.

The experiments in the paper were performed using [EASIER](http://sealabtools.di.univaq.it/EASIER/), which is available in a different repository:

[https://github.com/SEALABQualityGroup/EASIER](https://github.com/SEALABQualityGroup/EASIER)

The data gathered during such experiments is provided here, in the [data](data) folder.
