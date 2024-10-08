#!/bin/bash

clear

DNAME="gcloud"
DNAME_REQ=".${DNAME}"

# Color Variables for text
GREEN='\033[0;32m'
PURPLE='\033[1;34m'
PINK='\033[0;35m'
LIGHTBLUE_BOLD='\033[1;36m'
CYAN='\033[1;96m'
MAGENTA='\033[1;95m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
BLINK='\033[5m'

NC='\033[0m' # No Color

DNAME_LOWER=$(echo "$DNAME" | tr '[:upper:]' '[:lower:]')

dev_env_setup() {
    echo "Building Dev Environment for VS Code"
    #Clear the terminal
    clear

    # Get the directory where the script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" # get the directory where the script is located ... full path

    # Get the name of the folder where the script is located
    CURRENT_DIR=$(basename "$SCRIPT_DIR")

    # Print the directory and current folder name
    echo "SCRIPT_DIR: $SCRIPT_DIR"
    echo "CURRENT_DIR: $CURRENT_DIR"

    # Change to that directory
    cd "${SCRIPT_DIR}" || exit 1

    # Name of the virtual environment
    VENV_NAME="${CURRENT_DIR}_venv"

    # Form the name of the virtual environment directory
    VENV_DIR="${SCRIPT_DIR}/${VENV_NAME}"
    echo -e "Virtual environment directory: ${VENV_DIR}\033[0m"

    # Full path to the virtual environment directory
    FULL_VENV_PATH="${SCRIPT_DIR}/${VENV_NAME}"
    echo -e "Full path to virtual environment directory: ${FULL_VENV_PATH}\033[0m"

    # Delete the directory
    rm -rf "${FULL_VENV_PATH}"

    # Create a new virtual environment
    python3 -m venv "/${FULL_VENV_PATH}" || {
        echo -e "\033[1;31mCreating virtual environment at ${FULL_VENV_PATH} failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mVirtual environment created successfully\033[0m"

    # Change directory
    cd ${FULL_VENV_PATH} || {
        echo -e "\033[1;31mChanging directory failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mChanged directory successfully\033[0m"

    # Activate the virtual environment
    source "${FULL_VENV_PATH}/bin/activate" || {
        echo -e "\033[1;31mActivating virtual environment failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mActivated virtual environment successfully\033[0m"

    # Get the path of the requirements file
    REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements${DNAME_REQ}.txt"
    echo "Requirements file: $REQUIREMENTS_FILE"

    # Upgrade pip
    pip install --upgrade pip || {
        echo -e "\033[1;31mPip upgrade failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mPip upgrade successful\033[0m"

    # Install requirements
    echo -e "\n\n\033[4;32mProceeding with the installation of all libraries ...\033[0m"
    pip install -r ${REQUIREMENTS_FILE} || {
        echo -e "\033[1;31mRequirements installation failed\033[0m"
        exit 1
    }

    echo -e "\033[1;32mRequirements installation successful\033[0m"

    # ### Change to that directory
    cd "${SCRIPT_DIR}" || exit 1
    # ### Backup current requirements
    mkdir -p .req_backup
    cp ${REQUIREMENTS_FILE} ".req_backup/requirements_raw_$(date +%Y%m%d_%H%M%S).txt" || {
        echo -e "\033[1;31mRequirements backup failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mRequirements backup successful\033[0m"

    # ### Freeze the current state of packages
    pip freeze >".req_backup/requirements_freeze_$(date +%Y%m%d_%H%M%S).txt" || {
        echo -e "\033[1;31mFreezing requirements failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mFreezing requirements successful\033[0m"

    #Downloading Spacy model
    python -m spacy download en_core_web_sm
    brew install tesseract

    # Installing NLTK libraries
    # install_nltk_libraries

    # Run Playwright install command to download necessary browsers
    playwright install
    sudo pip install firebase-admin

    echo -e "\033[5;32mInstallation complete\033[0m"

}

install_nltk_libraries() {

    # Run Python commands to download NLTK data
    python3 -c "
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('maxent_ne_chunker')
nltk.download('maxent_ne_chunker_tab')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
"
}

dev_env_setup
