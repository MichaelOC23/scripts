#!/bin/bash

SCRIPTS="${HOME}/code/mytech/docker/Utils/scripts"
VENV_PATH="${SCRIPTS}/scripts_venv/bin/activate"
SCRIPT_PATH="${SCRIPTS}/_py2_prepend_filename_to_extracts.py"

# Check if the first parameter is provided
if [ -n "$1" ]; then
    # If a parameter is provided, use it
    target_dir="$1"
else
    # If no parameter is provided, use the current working directory
    target_dir="$(pwd)"
fi

echo -e "Sourcing the Virtual environment: ${VENV_PATH}"
source "${VENV_PATH}"
# Running the script in the current directory
echo -e "Running the script \n python3 ${SCRIPT_PATH} \n ${target_dir}"
echo -e "Writing output to ${target_dir}/add_title_log.txt"
python3 "${SCRIPT_PATH}" "${target_dir}" >"${PWD}/add_title_log.txt"

echo -e "File Name Append Complete"
