#!/bin/bash

python model_runner.py 30 scenarios/cu-50-nisol-bars-only.json
python model_runner.py 30 scenarios/cu-50-nisol-restaurants-only.json
python model_runner.py 30 scenarios/cu-50-nisol-phase-three.json
