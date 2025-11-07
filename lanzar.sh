#!/bin/bash

echo "Starting APP"

if [[ -d venv ]]
then
    echo "previous python environment exists, deleting..."
    rm -r venv
fi
echo "Generating and activating the environment"
python3 -m venv venv

source venv/bin/activate
python -m pip install --upgrade pip
cd src
pip install -r requirements.txt -U
echo "================================================"
echo "Showing the python we are using (should be the one from the env)"
which python
python --version
echo "================================================"
echo "Showing installed packages"
pip freeze > ../requirements_freeze.txt
echo "================================================"
echo "Launching the APP"
python MAIN.py

echo " Finalizado"
