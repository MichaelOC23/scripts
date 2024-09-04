#!/bin/bash

clear

DNAME="Communify"
DPATH="${HOME}/code/mytech/docker/Communify"
DPORT=4001

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

docker_build_and_run() {
    cd "${DPATH}" || exit 1

    # Stop and remove the existing container if it exists
    if [ "$(docker ps -q -f name=${DNAME_LOWER}-container)" ]; then
        echo "Stopping existing container..."
        docker stop "${DNAME_LOWER}-container"
    fi

    if [ "$(docker ps -aq -f name=${DNAME_LOWER}-container)" ]; then
        echo "Removing existing container..."
        docker rm "${DNAME_LOWER}-container"
    fi

    #build the Docker container
    docker_build

    # Run the Docker container
    echo "Running Docker container..."

    docker_run

    echo "Docker build and run complete for ${DNAME}"
}

docker_run() {
    cd "${DPATH}"
    echo -e "Docker RUN for DNAME=${DNAME}; DPORT=${DPORT} DNAME_LOWER=${DNAME_LOWER}"
    docker run -d -p "${DPORT}:${DPORT}" --name "${DNAME_LOWER}-container" \
        -e OFFICE365_BACKGROUND_PORT="${OFFICE365_BACKGROUND_PORT}" \
        -e AZURE_APP_CLIENT_ID="${AZURE_APP_CLIENT_ID}" \
        -e AZURE_APP_TENANT_ID="${AZURE_APP_TENANT_ID}" \
        "${DNAME_LOWER}-app"
    echo "Docker RUN complete for ${DNAME}"
    exit 0
}

docker_build() {
    cd "${DPATH}"
    echo "Docker BUILD for ${DNAME}"
    docker build -t "${DNAME_LOWER}-app" .
    echo "Docker BUILD complete for ${DNAME}"
}

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
    REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.${DNAME}.txt"
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

    echo -e "\033[5;32mInstallation complete\033[0m"

}

# Function to display the menu
show_menu() {
    echo -e "${BOLD}Please choose one of the following options (enter the number):\n"
    echo -e "${BOLD}|-------------------------------------------------------------|${NC}\n"
    echo -e "${BOLD}1) Docker ${MAGENTA}RUN ${BOLD}${DNAME} ${NC}"
    echo -e "${MAGENTA}2) Docker ${LIGHTBLUE_BOLD}BUILD ${BOLD}and ${MAGENTA}RUN ${BOLD}${DNAME} ${NC}"
    echo -e "${BOLD}3)Build Dev Environment for VS Code ${NC}"
    echo -e "${BOLD} Press Enter to exit ${NC}"
}

# Function to read the user's choice
read_choice() {
    local choice
    read -p "Enter choice [0 - 10]: " choice
    case $choice in

    1)
        docker_run
        ;;
    2)
        docker_build_and_run
        ;;
    3)
        echo "Building Dev Environment for VS Code"
        dev_env_setup
        exit 0
        ;;
    *)
        echo "Exiting..."
        exit 0
        ;;
    esac
}

# Function to read the user's choice
while true; do
    show_menu
    read_choice
done
