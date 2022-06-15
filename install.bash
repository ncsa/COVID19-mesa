#!/bin/bash

# Santiago Nunez-Corrales and Eric Jakobsson
# University of Illinois at Urbana-Champaign

# This script assumes a new Amazon EC2 instance
# c5a.8xlarge with no prior usage.

sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip
sudo update-alternatives --config python
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 10
pip3 install --upgrade pip
sudo update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10
git clone https://github.com/snunezcr/COVID19-mesa.git
cd COVID19-mesa/
cd outcomes/
rm -rf *
cd ..
python -m pip install -r requirements.txt 
python -m pip install pandas
python -m pip install tqdm
python -m pip install mesa
python -m pip install scipy
pip install matplotlib

