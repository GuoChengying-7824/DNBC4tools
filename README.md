[![docs]([https://img.shields.io/static/v1?label=docs&message=dnbc4tools&color=green)](https://dnbc4tools.readthedocs.io/zh/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/dnbc4tools)](https://pypi.org/project/DNBC4tools)
[![Docker Pulls](https://img.shields.io/docker/pulls/lishuangshuang3/dnbc4tools)](https://hub.docker.com/r/lishuangshuang3/dnbc4tools)

# DNBelab_C_Series_HT_scRNA-analysis-software
An open source and flexible pipeline to analysis high-throughput DNBelab C Series single-cell RNA datasets
## Introduction
- **Propose**
  - An open source and flexible pipeline to analyze DNBelab C Series<sup>TM</sup> single-cell RNA datasets. 
- **Language**
  - Python3(>=3.8.*),R scripts
- **Hardware/Software requirements** 
  - x86-64 compatible processors.
  - require at least 50GB of RAM and 4 CPU. 
  - centos 7.x 64-bit operating system (Linux kernel 3.10.0, compatible with higher software and hardware configuration). 

## Directory contents
- **DNBC4tools**   config, software and script directories.
- **doc**   Instruction for use.
- **example** Example of use the pipline.
- **scripts**    Miscellaneous scripts.
- **wdl**  WDL pipeline.

## Installation
installation manual [**here**](./doc/installation.md)

## Database
Create database manual [**here**](./doc/database.md)
## Start

**Command line : Using the DNBC4tools**

- **[DNBC4tools](./doc/DNBC4tools/start.md)**

**Container**

- **[Docker/Singularity](./doc/docker/start.md)**

**WDL : Customize the config file, use wdl to analysis**

- **[WDL](./doc/wdl/start.md)**
