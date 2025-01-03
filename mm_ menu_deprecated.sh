#!/bin/bash

###### NEW SCRIPT #########


clear

# Key folders
CODE_PATH="${HOME}/code"

# # Communify Paths
# PLATFORM_PATH="${CODE_PATH}/platform"
# FRONTEND_PATH="${CODE_PATH}/frontend"

# Scripts Paths
SCRIPT_PATH="${CODE_PATH}/scripts"
SCRIPT_VENV_PATH="${SCRIPT_PATH}/scripts_venv/bin/activate"
SCRIPT_PYTHON_PATH="${SCRIPT_PATH}/scripts_venv/bin/python"

#Transcription Paths
#    /Users/michasmi/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/test/20221221 084237-36681A60.m4a
VOICE_MEMO_FOLDER="${HOME}/Library/Mobile Documents/iCloud~md~obsidian/Documents/_AudioRecordings"

# Color Variables for text
BLACK='\033[0;30m'
RED='\033[0;31m'
RED_U='\033[4;31m'
RED_BLINK='\033[5;31m'
GREEN='\033[0;32m'
GREEN_BLINK='\033[5;32m'
YELLOW='\033[0;33m'
YELLOW_BOLD='\033[1;33m'
PURPLE='\033[1;34m'
PURPLE_U='\033[4;34m'
PURPLE_BLINK='\033[5;34m'
PINK='\033[0;35m'
PINK_U='\033[4;35m'
PINK_BLINK='\033[5;35m'
LIGHTBLUE='\033[0;36m'
LIGHTBLUE_BOLD='\033[1;36m'
GRAY='\033[0;37m'
ORANGE='\033[1;91m'
BLUE='\033[1;94m'
CYAN='\033[1;96m'
WHITE='\033[1;97m'
MAGENTA='\033[1;95m'
BOLD='\033[1m'
UNDERLINE='\033[4m'
BLINK='\033[5m'
NC='\033[0m' # No Color



PS3="Enter your choice: " # Prompt string for select

OPTION00="Commit the current folder's git repo ${NC}"
commit_current_folder_menu() {
    commit_current_folder
    exit 0
}

OPTION01="Extract and clean text from all PDFs (recursive)${CYAN} Gemini${NC} <start dir>  ${NC}"
extract_and_clean_text_menu() {
    extract_and_clean_text_from_pdfs
    exit 0
}

OPTION02="Summarize all clean text extracts (recursive)${CYAN} Gemini${NC} <start dir>  ${NC}"
OPTION03="Transcribe new Voicememos ${NC}"
OPTION04="Transcribe recordings in folder${NC} <start dir> ${NC}"
OPTION05="Force Ollama Restart ${NC}"
OPTION06="Force Kill Ollama ${NC}"
OPTION07="Kill all Python processes ${NC}"
OPTION08="Stop-Restart Postgres ${NC}"
OPTION09="Install/Upgrade Open Web UI  ${NC}"
OPTION10="Set Ollama Env Variables (one-time)  ${NC}"
OPTION11="Update Local Secrets from Google Cloud ${NC}"
OPTION12="Stop/Restart Open Web UI  ${NC}"

options=("${OPTION00}" "${OPTION01}" "${OPTION02}" "${OPTION03}" "${OPTION04}" "${OPTION05}" "${OPTION06}" "${OPTION07}" "${OPTION08}" "${OPTION09}" "${OPTION10}" "${OPTION11}" "${OPTION12}")

select opt in "${options[@]}"; do
    case $opt in
    "${OPTION00}")
        echo -e "${OPTION00}"
        commit_current_folder_menu
        ;;
    "${OPTION01}")
        echo -e "${OPTION01}"
        extract_and_clean_text_menu
        ;;
    "${OPTION02}")
        echo -e "${OPTION02}"
        #placeholder
        ;;
    "${OPTION03}")
        echo -e "${OPTION03}"
        #placeholder
        ;;
    "${OPTION04}")
        echo -e "${OPTION04}"
        #placeholder
        ;;
    "${OPTION05}")
        echo -e "${OPTION05}"
        #placeholder
        ;;
    "${OPTION06}")
        echo -e "${OPTION06}"
        #placeholder
        ;;
    "${OPTION07}")
        echo -e "${OPTION07}"
        #placeholder
        ;;
    "${OPTION08}")
        echo -e "${OPTION08}"
        #placeholder
        ;;
    "${OPTION09}")
        echo -e "${OPTION09}"
        #placeholder
        ;;
    "${OPTION10}")
        echo -e "${OPTION10}"
        #placeholder
        ;;
    "${OPTION11}")
        echo -e "${OPTION11}"
        #placeholder
        ;;
    "${OPTION12}")
        echo -e "${OPTION12}"
        #placeholder
        ;;
    "Exit")
        echo -e "Exiting. Goodbye!"
        break
        ;;
    *)
        echo -e "Exiting. Goodbye!"
        break
        ;;
    esac
done
exit 0

# Function to display the menu
show_menu() {

}








##########################
#####    OLD SCRIPT ######
##########################




# Function to read the user's choice
read_choice() {
    local choice
    read -p "Enter choice [0 - 10]: " choice
    case $choice in
    0)
        commit_current_folder
        exit 0
        ;;
    1)
        commit_mytech
        exit 0
        ;;

    2)
        # Get a list of all ollama processes and kill them
        echo -e "Killing all Ollama Processes and restarting..."
        pkill -f ollama
        # Check if there are any remaining ollama processes
        sleep 1
        if pgrep -f ollama >/dev/null; then
            echo -e "Some ollama processes could not be terminated."
            echo -e "Waiting 3 seconds and trying again ..."
            sleep 3
            echo -e "2nd Attempt: killing all ollama processes..."
            pkill -f ollama
            sleep 3
            if pgrep -f ollama >/dev/null; then
                echo -e "After the 2nd attempt, some ollama processes still could not be terminated"
                echo -e "Please check and manually terminate any remaining ollama processes."
            fi
        else
            echo "All ollama processes have been successfully terminated. \n Restarting Ollama"
            sleep 3
            ollama serve &

        fi
        exit 0
        ;;
    3)
        # Get a list of all ollama processes and kill them
        echo -e "Killing all Ollama Processes . . ."
        pkill -f ollama
        # Check if there are any remaining ollama processes
        sleep 1
        if pgrep -f ollama >/dev/null; then
            echo -e "Some ollama processes could not be terminated."
            echo -e "Waiting 3 seconds and trying again ..."
            sleep 3
            echo -e "2nd Attempt: killing all ollama processes..."
            pkill -f ollama
            sleep 3
            if pgrep -f ollama >/dev/null; then
                echo -e "After the 2nd attempt, some ollama processes still could not be terminated"
                echo -e "Please check and manually terminate any remaining ollama processes."
            fi
        fi
        exit 0
        ;;

    4) ;;
    5)
        summarize_and_tag_pdfs
        exit 0
        ;;
    6)
        start_listgen
        exit 0
        ;;
    7)
        transcribe_named_folder
        exit 0
        ;;
    8)
        transcribe_new_voice_memos
        exit 0
        ;;
    9)
        # Get a list of all Python processes and kill them
        echo -e "Killing all Python processes..."
        pkill -f python
        # Check if there are any remaining Python processes
        sleep 1
        if pgrep -f python >/dev/null; then
            echo -e "Some Python processes could not be terminated."
            echo -e "Waiting 3 seconds and trying again ..."
            sleep 3
            echo -e "2nd Attempt: killing all Python processes..."
            pkill -f python
            sleep 1
            if pgrep -f python >/dev/null; then
                echo -e "After the 2nd attempt, some Python processes still could not be terminated"
                echo -e "Please check and manually terminate any remaining Python processes."
            fi
        else
            echo "All Python processes have been successfully terminated."
        fi
        exit 0
        ;;
    10)
        find_duplicate_folders
        exit 0
        ;;

    11)
        echo "Restarting Postgres 14"
        brew services restart postgresql@14
        echo "Postgres 14 restarted"
        exit 0
        ;;
    12)

        install_or_upgrade_cask docker
        install_or_upgrade_cask ollama
        open -a Docker
        ;;
    13)

        source env_variables_ollama.sh
        exit 0
        ;;
    14)
        #Update Google Cloud Secrets
        echo -e "Updating secrets from Google Cloud"
        update_secrets_google_cloud
        echo -e "Local secrets have been updated."
        exit 0
        ;;
    15)
        # Fixed Variables
        HOST_OPTION="--add-host=host.docker.internal:host-gateway"
        LLM_DATA="${HOME}/data-llm"
        mkdir -p "${LLM_DATA}"

        # # Process the main open-webui image
        CONTAINER_NAME="open-webui"
        IMAGE_NAME="ghcr.io/open-webui/open-webui:main"
        OPENWEBUI_PORT_MAPPING="3000:8080"
        OPENWEBUI_DATA="${LLM_DATA}/open-webui-data"
        mkdir -p "${OPENWEBUI_DATA}"
        OPENWEBUI_VOLUME_MAPPING="${OPENWEBUI_DATA}:/app/backend/data"
        echo -e "Stopping and removing any OPEN-WEBUI container..."
        stop_and_remove_container
        echo -e "Checking for image updates..."
        pull_latest_image
        echo -e "Starting a new container..."
        run_container_openwebui

        CONTAINER_NAME="pipelines"
        IMAGE_NAME="ghcr.io/open-webui/pipelines:main"
        OPENWEBUI_PIPELINE_DATA="${LLM_DATA}/open-webui-data/pipelines"
        mkdir -p "${OPENWEBUI_PIPELINE_DATA}"
        echo -e "Stopping and removing any existing PIPELINE container..."
        stop_and_remove_container
        echo -e "Checking for PIPELINE image updates..."
        pull_latest_image
        echo -e "Starting a new PIPELINE container..."
        run_container_pipeline

        # CONTAINER_NAME="whisper-docker"
        # WHISEPER_LLM_DATA="${HOME}/data-llm/whisper"
        # mkdir -p "${WHISEPER_LLM_DATA}"
        # IMAGE_NAME="ghcr.io/appleboy/go-whisper:latest"
        # echo -e "Stopping and removing any existing WHISPER container..."
        # stop_and_remove_container
        # echo -e "Checking for WHISPER image updates..."
        # pull_latest_image
        # echo -e "Starting a new WHISPER container..."
        # run_container_whisper

        echo "Container setup complete."
        exit 0

        ;;

    901)
        echo -e "Removing and recreating the virtual environment ..."
        venv_rm_and_recreate
        exit 0
        ;;
    902)
        # Get a list of all Python processes and kill them
        echo -e "Killing all Python processes..."
        pkill -f python
        # Check if there are any remaining Python processes
        sleep 1
        if pgrep -f python >/dev/null; then
            echo -e "Some Python processes could not be terminated."
            echo -e "Waiting 3 seconds and trying again ..."
            sleep 3
            echo -e "2nd Attempt: killing all Python processes..."
            pkill -f python
            sleep 1
            if pgrep -f python >/dev/null; then
                echo -e "After the 2nd attempt, some Python processes still could not be terminated"
                echo -e "Please check and manually terminate any remaining Python processes."
            fi
        else
            echo "All Python processes have been successfully terminated."
        fi
        exit 0
        ;;

    904)
        display_color_palette
        exit 0
        ;;
    905)
        echo "Granting terminal access to iCloud Drive"
        tccutil reset SystemPolicyDocumentsFolder
        sudo tccutil reset SystemPolicyDocumentsFolder
        sudo tccutil reset All
        echo "Terminal access to iCloud Drive granted"
        exit 0
        ;;

    *)
        echo "Invalid choice. Exiting ..."
        exit 0
        ;;
    esac
}

#! BUSINESS / DEV SCRIPTS
deinitialize_git_repo() {
    if [ -d "$1/.git" ]; then
        # Remove the .git folder to de-initialize the repository
        rm -rf "$1/.git"
        cp /Volumes/code/vscode/code-admin/scripts/gitignore_template $1/.gitignore
        echo "$1 has been de-initialized and the .gitignore file has been reset to the template version."
    fi
}

find_duplicate_folders() {
    folder_path=$(pwd)
    start_scripts_venv # Start the Python Virtual Environment
    python "${SCRIPT_PATH}/>find_duplicate_files2.py" "$folder_path"

}

update_secrets_google_cloud() {
    start_scripts_venv # Start the Python Virtual Environment
    python "${SCRIPT_PATH}/_100_update_secrets.py"

}

commit_current_folder() {
    echo -e "Committing changes to current repository at: $PWD"
    git pull origin main
    git add .
    git commit -m "default commit message"
    git push origin main

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Commit Successful for ${PWD} ${NC}"
    else
        echo -e "${RED}!! ERROR !! Commit was not successful${NC}"
    fi
}

commit_mytech() {
    echo -e "Committing and pushing MyTech ..."
    cd "${HOME}/code/mytech" || {echo "Error: '${HOME}/code/mytech' directory not found." exit 1
    commit_current_folder
    cd "${HOME}"
    echo -e "Complete and pushed of MyTech is complete."
}

extract_and_clean_text_from_pdfs() {
    response=$(get_input_or_default "Enter the directory to start the recursive text extraction and cleaning. Press enter to start in the current directory.")
    echo -e "Extracting and cleaning text (recursively)\n$response"
    start_scripts_venv
    python _01c_extract_name_and_clean.py "$response"
    echo -e "Text extraction is complete."
}

transcribe_named_folder() {
    response=$(get_input_or_default "Enter the directory with the audio recordings. \nPress enter to start in the current directory. ")
    echo -e "Beginning conversion and transcription in \n$response "
    _04a_transcribe_folder_m4a_to_mp3_to_deep.sh $response
    echo -e "Transcription complete."
}

transcribe_new_voice_memos() {
    echo -e "Beginning conversion and transcription in ${VOICE_MEMO_FOLDER}"
    _04a_transcribe_folder_m4a_to_mp3_to_deep.sh "$VOICE_MEMO_FOLDER"
    echo -e "Transcription of voice memos is complete."
}

summarize_and_tag_pdfs() {
    response=$(get_input_or_default "Enter the directory to start the summarizatioin and tagging. \nPress enter to start in the current directory. ")
    echo -e "Summarizing and tagging (recursively)\n$response "
    start_scripts_venv
    python _02b_summarize_and_tag_with_gemini.py $response
    echo -e "Text extraction is complete."
}

venv_rm_and_recreate() {
    echo "Building Dev Environment for VS Code"
    #Clear the terminal
    clear

    # Get the directory where the script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" # get the directory where the script is located ... full path
    CURRENT_DIR=$(basename "$PWD")

    echo -e "Script directory: ${SCRIPT_DIR}\033[0m"
    echo -e "Current directory: ${CURRENT_DIR}\033[0m"

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
    REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.${CURRENT_DIR}.txt"
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

    echo -e "\033[5;32mInstallation complete\033[0m"

}

display_color_palette() {
    echo "Examples of Font Colors in Bash"
    echo -e "${BLACK}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${RED}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${RED_U}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${RED_BLINK}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${GREEN}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${GREEN_BLINK}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${YELLOW}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${PURPLE}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${PURPLE_U}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${PURPLE_BLINK}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${PINK}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${PINK_U}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${PINK_BLINK}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
    echo -e "${LIGHTBLUE}The Quick Brown Fox Jumped Over the Lazy Dog ${NC}"
}

#! SUPPORTING UTILITIES

kill_process_by_name() {
    #${PROCESS_NAME}
    # Get a list of all Python processes and kill them
    echo -e "Killing all ${PROCESS_NAME} processes..."
    pkill -f "${PROCESS_NAME}"
    # Check if there are any remaining ${PROCESS_NAME} processes
    sleep 1
    if pgrep -f "${PROCESS_NAME}" >/dev/null; then
        echo -e "Some ${PROCESS_NAME} processes could not be terminated."
        echo -e "Waiting 3 seconds and trying again ..."
        sleep 3
        echo -e "2nd Attempt: killing all ${PROCESS_NAME} processes..."
        pkill -f "${PROCESS_NAME}"
        sleep 1
        if pgrep -f "${PROCESS_NAME}" >/dev/null; then
            echo -e "After the 2nd attempt, some ${PROCESS_NAME} processes still could not be terminated"
            echo -e "Please check and manually terminate any remaining ${PROCESS_NAME} processes."
        fi
    else
        echo "All Python processes have been successfully terminated."
    fi
    exit 0
}

# Function to prompt the user and return a value or default to current directory
get_input_or_default() {
    local prompt="$1"
    local default_value="${2:-$(pwd)}" # Default value is current directory if not provided

    read -p "${prompt}" user_input
    if [ -z "$user_input" ] || [ "$user_input" = "pwd" ] || [ "$user_input" = "." ]; then
        echo "$default_value"
    else
        echo "$user_input"
    fi
}

# Function to install or upgrade Homebrew packages
install_or_upgrade() {
    if brew list --formula | grep -q "^$1\$"; then
        echo "Upgrading $1..."
        brew upgrade $1
    else
        echo "Installing $1..."
        brew install $1
    fi
}

# Function to install or upgrade Homebrew casks
install_or_upgrade_cask() {
    if brew list --cask | grep -q "^$1\$"; then
        echo "Upgrading $1..."
        brew upgrade --cask $1
    else
        echo "Installing $1..."
        brew install --cask $1
    fi
}

#! DOCKER UTILITIES
# Function to pull the latest Docker image
pull_latest_image() {
    echo "Pulling the latest image: $IMAGE_NAME"
    docker pull "$IMAGE_NAME"
}

# Function to stop and remove the container if it exists
stop_and_remove_container() {
    if docker ps -q -f name="$CONTAINER_NAME" >/dev/null; then
        echo "Stopping running container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
    fi

    if docker ps -aq -f name="$CONTAINER_NAME" >/dev/null; then
        echo "Removing existing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
    fi
}

run_container_openwebui() {
    docker run -d \
        -p "${OPENWEBUI_PORT_MAPPING}" \
        "${HOST_OPTION}" \
        -v "${OPENWEBUI_VOLUME_MAPPING}" \
        --env=OLLAMA_BASE_URL=http://host.docker.internal:11434 \
        --env=USE_EMBEDDING_MODEL_DOCKER=sentence-transformers/all-MiniLM-L6-v2 \
        --env=USE_RERANKING_MODEL_DOCKER= \
        --env=OPENAI_API_BASE_URL= \
        --env=OPENAI_API_KEY="${OPENAI_API_KEY}" \
        --env=WEBUI_SECRET_KEY= \
        --env=SCARF_NO_ANALYTICS=true \
        --env=DO_NOT_TRACK=true \
        --env=ANONYMIZED_TELEMETRY=false \
        --env=WHISPER_MODEL=base \
        --env=WHISPER_MODEL_DIR=/app/backend/data/cache/whisper/models \
        --env=RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
        --env=RAG_RERANKING_MODEL= \
        --env=SENTENCE_TRANSFORMERS_HOME=/app/backend/data/cache/embedding/models \
        --env=HF_HOME=/app/backend/data/cache/embedding/models \
        --env=DOCKER=true \
        --name "${CONTAINER_NAME}" \
        --restart always \
        "${IMAGE_NAME}"
}

run_container_pipeline() {
    OPENWEBUI_BACKEND_DATA="${LLM_DATA}/open-webui-data/backend"
    docker run -d -p 9099:9099 \
        "${HOST_OPTION}" \
        -v "${OPENWEBUI_PIPELINE_DATA}:/app/pipelines" \
        -v "${OPENWEBUI_BACKEND_DATA}:/app/backend" \
        --env=PIPELINES_REQUIREMENTS_PATH=/app/pipelines/requirements.pipelines.txt \
        --name "${CONTAINER_NAME}" \
        --restart always \
        ghcr.io/open-webui/pipelines:main
    # docker run -d -p 9099:9099 --add-host=host.docker.internal:host-gateway -v pipelines:/app/pipelines --name pipelines --restart always ghcr.io/open-webui/pipelines:main

}

run_container_whisper() {
    docker run -d -p 9099:9099 \
        $HOST_OPTION \
        -v $WHISEPER_LLM_DATA/models:/app/models \
        -v $WHISEPER_LLM_DATA/testdata:/app/testdata \
        --env MODEL=/app/models/ggml-small.bin \
        --name "$CONTAINER_NAME" \
        --restart always \
        "$IMAGE_NAME"

}

#! MENU UTILITIES
# Function to ask for confirmation
confirm() {
    while true; do
        read -p "$1 ( ${PURPLE}Yy or ${PINK_U}Nn ${NC}): " yn
        case $yn in
        [Yy]*) return 0 ;;                                                     # User responded yes
        [Nn]*) return 1 ;;                                                     # User responded no
        *) echo "${RED_BLINK}Please answer Y for 'yes' or N for 'no'.${NC}" ;; # Invalid response
        esac
    done
}

# Main logic loop
while true; do
    show_menu
    read_choice
done



# OPTIONX="Start/Restart ListGen ${NC}"
# OPTIONX="Find duplicate folders (recursive)${NC} <start dir> or current dir${NC}"
# OPTIONX="Commit and Push MyTech${NC}"

# echo -e "\n\n${LIGHTBLUE_BOLD}Hello! What would you like to do?"
# echo -e "Please choose one of the following options (enter the number):\n"
# echo -e "|---------------------    BUSINESS TOOLS    -------------------|${NC}\n"
# echo -e "${MAGENTA} 0) Commit the current folder's git repo ${NC}"
# echo -e "${MAGENTA} 1) Commit and Push MyTech${NC}"
# echo -e "${MAGENTA} 4) Extract and clean text from all PDFs (recursive)${CYAN} Gemini${NC} <start dir>  ${NC}"
# echo -e "${MAGENTA} 5) Summarize all clean text extracts (recursive)${CYAN} Gemini${NC} <start dir>  ${NC}"
# echo -e "${MAGENTA} 8) Transcribe new Voicememos ${NC}"
# echo -e "${MAGENTA} 7) Transcribe recordings in folder${NC} <start dir> ${NC}"
# echo -e "${MAGENTA} 6) Start/Restart ListGen ${NC}"
# echo -e "${MAGENTA}10) Find duplicate folders (recursive)${NC} <start dir> or current dir${NC}"

# echo -e "|---------------------    APPLICATIONS    -------------------|${NC}\n"
# echo -e "${MAGENTA} 2) Force Ollama Restart ${NC}"
# echo -e "${MAGENTA} 3) Force Kill Ollama ${NC}"
# echo -e "${MAGENTA} 9) Kill all Python processes ${NC}"

# echo -e "|---------------------    SETUP    -------------------|${NC}\n"
# echo -e "${MAGENTA}11) Stop-Restart Postgres ${NC}"
# echo -e "${CYAN}12) Install/Upgrade Open Web UI  ${NC}"
# echo -e "${CYAN}13) Set Ollama Env Variables (one-time)  ${NC}"
# echo -e "${CYAN}14) Update Local Secrets from Google Cloud ${NC}"
# echo -e "${MAGENTA}15) Stop/Restart Open Web UI  ${NC}"
# # echo -e "${LIGHTBLUE}>>> XXX) Display color palette${NC}"
# # echo -e "${MAGENTA}XX) Copy files by type (recursive)${NC} <.XXX> <from dir> <to dir> ${NC}"