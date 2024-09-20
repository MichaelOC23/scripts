#!/bin/bash

# Check if at least one argument (the Python script) is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <python_script> [arg1] [arg2]"
    exit 1
fi

# Path to the Python script
PYTHON_SCRIPT=$1

source "${HOME}/code/scripts/env_variables.sh"

# Optional parameters for the Python script
ARG1=${2:-}
ARG2=${3:-}

# Path to the virtual environment
VENV_PATH="${HOME}/code/scripts/scripts_venv"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

cd "${HOME}/code/scripts/_live"

# Run the Python script with up to two optional parameters using the venv's Python
"$VENV_PATH/bin/python" "$PYTHON_SCRIPT" "$ARG1" "$ARG2"

# Deactivate the virtual environment
deactivate
