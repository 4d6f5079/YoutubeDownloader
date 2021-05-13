#!/bin/bash

NAME_VENV_DIR="venv"

python -m venv ${NAME_VENV_DIR}
source venv/Scripts/activate
pip install -r requirements.txt