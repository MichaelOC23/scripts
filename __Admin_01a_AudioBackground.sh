#!/bin/bash

main() {

    WORKING_DIR="${HOME}/code/mytech/docker/AudioBackground"
    CLASSES_DIR="${HOME}/code/mytech/classes"

    STREAMLIT_APP="000_Meeting_Tech.py"
    QUART_APP="AudioBackground"

    PROD_VENV="AudioBackground_Prod_venv"
    DEV_VENV="AudioBackground_venv"

    STREAMLIT_PORT=4002
    QUART_PORT=4003

    # Export environment variables
    export QUART_APP=AudioBackground
    export QUART_ENV=production
    export SECRET_KEY="${ROTATING_ENCRYPTION_KEY}" # Ensure this is set in your shell environment
    export DEEPGRAM_API_KEY="${DEEPGRAM_API_KEY}"  # Ensure this is set in your shell environment

    CHOICE1="1) Launch Production AudioBackground and Meeting Tech Applications"
    CHOICE2="2) Reinstall Virtual Environment: DEVELOPMENT"
    CHOICE3="3) Reinstall Virtual Environment: PRODUCTION"
    CHOICE4="4) Initialize complete install/reinstall/upgrade of homebrew, portaudio, ffmpeg and virtual environments"

    echo -e "\033[1;32mAdmin tools for: AudioBackground and Meeting Tech.\033[0m"
    echo -e "${CHOICE1}\n${CHOICE2}\n${CHOICE3}\n${CHOICE4}\n"

    
    local choice
    read -p "Enter choice number (1, 2, 3, etc.): " choice
    case $choice in
    1)
        echo -e "$CHOICE1"
        launch_prod

        echo -e "\033[1;32m *FINISHED* \033[0m"
        ;;

    2)
        echo -e "$CHOICE2"
        VENV_FOLDER_NAME=$DEV_VENV
        delete_virtual_environment
        install_venv

        echo -e "\033[1;32m *FINISHED* \033[0m"
        ;;

    3)
        echo -e "$CHOICE3"
        VENV_FOLDER_NAME=$PROD_VENV

        # Ensure that the processes are stopped
        ensure_process_stopped "${STREAMLIT_PORT}" # Streamlit
        ensure_process_stopped "${QUART_PORT}"     # Quart / Deepgram

        delete_virtual_environment
        install_venv

        echo -e "\033[1;32m *FINISHED* \033[0m"
        ;;

    4)
        echo -e "$CHOICE4"
        install_homebrew
        install_portaudio
        install_ffmpeg

        VENV_FOLDER_NAME="${DEV_VENV}"
        delete_virtual_environment
        install_venv

        VENV_FOLDER_NAME="${PROD_VENV}"
        delete_virtual_environment
        install_venv

        echo -e "\033[1;32m *FINISHED* \033[0m"
        ;;
    *)
        echo "Exiting..."
        exit 0
        ;;

    esac
}

create_symbolic_link_for_classes() {
    # Check if the symbolic link exists
    cd "$WORKING_DIR"
    if [ -L "classes" ]; then
        echo "Symbolic link 'classes' already exists."
        return
    else
        echo "Creating symbolic link for classes..."
        ln -s "$CLASSES_DIR" classes
    fi

}

install_homebrew() {
    # Check if Homebrew is installed, if not, install it
    if ! command -v brew &>/dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >>/Users/$(whoami)/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo "Homebrew is already installed. Updating Homebrew..."
        brew update
    fi
}

install_portaudio() {
    # Install or upgrade portaudio
    if brew ls --versions portaudio >/dev/null; then
        echo "Portaudio is already installed. Upgrading portaudio..."
        brew upgrade portaudio
    else
        echo "Installing portaudio..."
        brew install portaudio
    fi
}

install_ffmpeg() {
    # Install or upgrade ffmpeg
    if brew ls --versions ffmpeg >/dev/null; then
        echo "ffmpeg is already installed. Upgrading ffmpeg..."
        brew upgrade ffmpeg
    else
        echo "Installing ffmpeg..."
        brew install ffmpeg
    fi
}

delete_virtual_environment() {
    # Delete the virtual environment
    echo -e "\033[1;31mDeleting the virtual environment\033[0m"
    rm -rf "${WORKING_DIR}/${VENV_FOLDER_NAME}"
}

install_venv() {
    # Create a new virtual environment

    create_symbolic_link_for_classes

    python3 -m venv "${WORKING_DIR}/${VENV_FOLDER_NAME}" || {
        echo -e "\033[1;31mCreating virtual environment at ${WORKING_DIR}/${VENV_FOLDER_NAME} failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mVirtual environment created successfully\033[0m"

    # Change directory
    cd "${WORKING_DIR}/${VENV_FOLDER_NAME}" || {
        echo -e "\033[1;31mChanging directory failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mChanged directory successfully\033[0m"

    # Activate the virtual environment
    source "${WORKING_DIR}/${VENV_FOLDER_NAME}/bin/activate" || {
        echo -e "\033[1;31mActivating virtual environment failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mActivated virtual environment successfully\033[0m"

    # Upgrade pip
    pip install --upgrade pip || {
        echo -e "\033[1;31mPip upgrade failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mPip upgrade successful\033[0m"

    # Install requirements
    echo -e "\n\n\033[4;32mProceeding with the installation of all libraries ...\033[0m"
    pip install -r "${WORKING_DIR}/requirements.AudioBackground.txt" || {
        echo -e "\033[1;31mRequirements installation failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mRequirements installation successful\033[0m"

    # Change to that directory
    cd "${WORKING_DIR}" || exit 1

    # Backup current requirements
    mkdir -p .req_backup
    cp "${WORKING_DIR}/requirements.AudioBackground.txt" ".req_backup/requirements_raw_$(date +%Y%m%d_%H%M%S).txt" || {
        echo -e "\033[1;31mRequirements backup failed\033[0m"
        exit 1
    }
    echo -e "\033[1;32mRequirements backup successful\033[0m"
}

ensure_process_stopped() {
    port="$1"

    # Debugging: Print the port value to check if it's correct
    echo "Debug: Port value is $port"

    # Check if the port value is a valid integer
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
        echo "Error: Port value '$port' is not a valid integer."
        exit 1
    fi

    # Check if process is already running on the specified port
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo -e "\033[1;95mProcess on port $port is already running. Killing it.\033[0m"
        # Debugging: Print the process ID before killing it
        pid=$(lsof -t -i:$port)
        echo "Process ID to be killed: $pid"
        if [ -n "$pid" ]; then
            kill -9 $pid
            if [ $? -eq 0 ]; then
                echo "Process $pid killed successfully."
            else
                echo "Failed to kill process $pid."
            fi
        else
            echo "No process found using port $port."
        fi
    else
        echo "No process is running on port $port."
    fi
}

launch_prod() {
    # Ensure that the processes are stopped
    ensure_process_stopped "${STREAMLIT_PORT}" # Streamlit
    ensure_process_stopped "${QUART_PORT}"     # Quart / Deepgram

    cd "${WORKING_DIR}"
    source "${WORKING_DIR}/${PROD_VENV}/bin/activate"

    # Run the Streamlit application in the foreground
    streamlit run "${STREAMLIT_APP}" --server.address 0.0.0.0 --server.port $STREAMLIT_PORT &
    echo -e "run ${STREAMLIT_APP} --server.address 0.0.0.0 --server.port ${STREAMLIT_PORT} &"

    # Run the Quart app with Hypercorn
    hypercorn "${QUART_APP}":app --bind "0.0.0.0:${QUART_PORT}" &
}

# Call the main function
main
