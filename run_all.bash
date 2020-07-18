#!/bin/bash

python model_runner.py 30 scenarios/cu-25-ntrace-nisol.json
python model_runner.py 30 scenarios/cu-25-ntrace-yisol.json
python model_runner.py 30 scenarios/cu-25-ytrace-nisol.json
python model_runner.py 30 scenarios/cu-25-ytrace-yisol.json
python model_runner.py 30 scenarios/cu-50-ntrace-nisol.json
python model_runner.py 30 scenarios/cu-50-ntrace-yisol.json
python model_runner.py 30 scenarios/cu-50-ytrace-nisol.json
python model_runner.py 30 scenarios/cu-50-ytrace-yisol.json
python model_runner.py 30 scenarios/cu-75-ntrace-nisol.json
python model_runner.py 30 scenarios/cu-75-ntrace-yisol.json
python model_runner.py 30 scenarios/cu-75-ytrace-nisol.json
python model_runner.py 30 scenarios/cu-75-ytrace-yisol.json
