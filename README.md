# Streaming Gradient Boosted Regression (SGBR)
- Paper: [Gradient boosted bagging for evolving data stream regression](https://doi.org/10.1007/s10618-025-01147-x)
# News
- **SGBR** is now available on latest [CapyMOA (Python)](https://github.com/adaptive-machine-learning/CapyMOA) (13/09/2025)
- **SGBR** is now available on latest [MOA (Java)](https://github.com/Waikato/moa) (30/08/2025)
# How to build the experiment setup
## Go to source root.
## Go to MOA source
``cd moa``
## Build MOA
`mvn clean install -DskipTests=true -Dmaven.javadoc.skip=true -Dlatex.skipBuild=true`
## Copy MOA jar to experiments folder
`cp .//target/moa-2023.04.1-SNAPSHOT-jar-with-dependencies.jar ../exp/moa.jar`


# Run experiments
## Setup
### Create conda environment with Python and Java (assumes its installed in the system)
``conda create -n SGBR python=3.9``
### go to exp folder
``cd exp``
### create output folders
``mkdir outout output_stats``
### go to dataset folder
``cd RDatasets``
### Unzip dataset files
``unzip hyperA.arff.zip``

``unzip DemandF.arff.zip``

``unzip NZEnergy.arff.zip``

plsease contact authors for copy of `SUP2I.arff`, `SUP3A.arff` and `SUP3G.arff`
### go level up (at exp)
``cd ..``
## Run Wall time experiments
```python benchmark_moa.py -f exp_config.json```
### Run periodic stats experiments
```python benchmark_moa.py -f exp_config_overTime.json```
### Run hyperparameter search experiments
```python benchmark_moa.py -f exp_config_SGBT_OZA_parameter_search.json```

```python benchmark_moa.py -f Plot_Hyper_LearningRate_FeatureP_twiny.py```

# Cite this work
```
@article{gunasekara2025gradient,
  title={Gradient boosted bagging for evolving data stream regression},
  author={Gunasekara, Nuwan and Pfahringer, Bernhard and Gomes, Heitor Murilo and Bifet, Albert},
  journal={Data mining and knowledge discovery},
  volume={39},
  number={5},
  pages={1--37},
  year={2025},
  doi={https://doi.org/10.1007/s10618-025-01147-x}
  publisher={Springer}
}
```

# MOA (Massive Online Analysis)
[![Build Status](https://travis-ci.org/Waikato/moa.svg?branch=master)](https://travis-ci.org/Waikato/moa)
[![Maven Central](https://img.shields.io/maven-central/v/nz.ac.waikato.cms.moa/moa-pom.svg)](https://mvnrepository.com/artifact/nz.ac.waikato.cms)
[![DockerHub](https://img.shields.io/badge/docker-available-blue.svg?logo=docker)](https://hub.docker.com/r/waikato/moa)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

![MOA][logo]

[logo]: http://moa.cms.waikato.ac.nz/wp-content/uploads/2014/11/LogoMOA.jpg "Logo MOA"

MOA is the most popular open source framework for data stream mining, with a very active growing community ([blog](http://moa.cms.waikato.ac.nz/blog/)). It includes a collection of machine learning algorithms (classification, regression, clustering, outlier detection, concept drift detection and recommender systems) and tools for evaluation. Related to the WEKA project, MOA is also written in Java, while scaling to more demanding problems.

http://moa.cms.waikato.ac.nz/

## Using MOA

* [Getting Started](http://moa.cms.waikato.ac.nz/getting-started/)
* [Documentation](http://moa.cms.waikato.ac.nz/documentation/)
* [About MOA](http://moa.cms.waikato.ac.nz/details/)

MOA performs BIG DATA stream mining in real time, and large scale machine learning. MOA can be extended with new mining algorithms, and new stream generators or evaluation measures. The goal is to provide a benchmark suite for the stream mining community. 

## Mailing lists
* MOA users: http://groups.google.com/group/moa-users
* MOA developers: http://groups.google.com/group/moa-development

## Citing MOA
If you want to refer to MOA in a publication, please cite the following JMLR paper: 

> Albert Bifet, Geoff Holmes, Richard Kirkby, Bernhard Pfahringer (2010);
> MOA: Massive Online Analysis; Journal of Machine Learning Research 11: 1601-1604 


