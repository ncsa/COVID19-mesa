#!/bin/bash

python model_runner.py 30 scenarios/cu-50-nisol-long.json
python model_runner.py 30 scenarios/cu-50-nisol-bars-only-long.json
python model_runner.py 30 scenarios/cu-50-nisol-restaurants-only-long.json
python model_runner.py 30 scenarios/cu-50-nisol-phase-three-long.json