#!/bin/bash

clear

# Key folders
CODE_PATH="${HOME}/code"
VOICE_MEMO_FOLDER="${HOME}/Library/Mobile Documents/iCloud~md~obsidian/Documents/_AudioRecordings"

# Scripts Paths
SCRIPT_PATH="${CODE_PATH}/scripts"
SCRIPT_VENV_PATH="${SCRIPT_PATH}/scripts_venv/bin/activate"
SCRIPT_PYTHON_PATH="${SCRIPT_PATH}/scripts_venv/bin/python"

# Color Variables for text
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[1;96m'
NC='\033[0m' # No Color

PS3="Enter your choice: " # Prompt string for select

start_scripts_venv(){
    source "${SCRIPT_VENV_PATH}"
}

# Menu Options and Functions
OPTION00="Commit the current folder's git repo"
commit_current_folder_menu() {
    commit_current_folder
    exit 0
}

OPTION01="Extract and clean text from all PDFs (recursive) Gemini <start dir>"
extract_and_clean_text_menu() {
    extract_and_clean_text_from_pdfs
    exit 0
}

OPTION02="Summarize all clean text extracts (recursive) Gemini <start dir>"
summarize_text_menu() {
    summarize_and_tag_pdfs
    exit 0
}

OPTION03="Transcribe new Voicememos"
transcribe_voicememos_menu() {
    transcribe_new_voice_memos
    exit 0
}

OPTION04="Transcribe recordings in folder <start dir>"
transcribe_recordings_menu() {
    transcribe_named_folder
    exit 0
}

OPTION05="Force Ollama Restart"
restart_ollama_menu() {
    kill_process_by_name "ollama"
    source "${SCRIPT_PATH}/env_start_ollama.sh"
    echo -e "${GREEN}Ollama restarted successfully.${NC} \n"
    echo -e "Available Ollama Models: \n" &
    ollama ls
    exit 0
}

OPTION06="Force Kill Ollama"
kill_ollama_menu() {
    kill_process_by_name "ollama"
    echo -e "${GREEN}All Ollama processes terminated.${NC}"
    exit 0
}

OPTION07="Kill all Python processes"
kill_python_menu() {
    kill_process_by_name "python"
    exit 0
}

OPTION08="Stop-Restart Postgres"
restart_postgres_menu() {
    echo "Restarting Postgres 14..."
    brew services restart postgresql@14
    echo "Postgres 14 restarted successfully."
    exit 0
}

OPTION09="Install/Upgrade Open Web UI"
install_open_web_ui_menu() {
    install_or_upgrade_cask "docker"
    install_or_upgrade_cask "ollama"
    echo -e "${GREEN}Open Web UI installed/upgraded successfully.${NC}"
    exit 0
}

OPTION10="Set Ollama Env Variables (one-time)"
set_ollama_env_menu() {
    source env_variables_ollama.sh
    echo -e "${GREEN}Ollama environment variables set successfully.${NC}"
    exit 0
}

OPTION11="Update Local Secrets from Google Cloud$"
update_google_secrets_menu() {
    source env_variables.sh
    update_secrets_google_cloud
    exit 0
}

OPTION12="Stop/Restart Open Web UI"
restart_open_web_ui_menu() {
    stop_and_remove_container
    pull_latest_image
    run_container_openwebui
    echo -e "${GREEN}Open Web UI restarted successfully."
    exit 0
}

OPTION13="Extract 5 rows from 1 csv file."
extract_5_rows_csv_file_menu(){
response=$(get_input_or_default "Enter the path to the CSV file")
    echo -e "Extracting 5 rows from: \n$response"
    extract_5_rows_csv_file $response
    python _02b_summarize_and_tag_with_gemini.py $response
    echo -e "Summarization complete."
}

OPTION14="Extract First Row of CSV Files in current folder"
extract_1_row_csv_folder_menu(){
    echo -e "asdf"
}

# Utility and Functional Definitions
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

extract_5_rows_csv_file() {
    
    # The filename is the first argument
    filename=$response

    # Use head to get the first 5 lines of the file
    head -n 5 "$filename" >"${filename%.csv}_first_5_rows.csv"
    echo "First 5 rows of $filename have been saved to ${filename%.csv}_first_5_rows.csv"
}

extract_1_row_csv_folder() {

    # Check if there are any CSV files in the current directory
    cd $response
    shopt -s nullglob
    csv_files=(*.csv)

    if [ ${#csv_files[@]} -eq 0 ]; then
        echo "This script should be run in the directory to inspect No CSV files found in the current directory."
        exit 1
    fi

    # Output file name where all data will be concatenated
    output_file="combined_output.txt"

    # Create or overwrite the output file
    : >"$output_file"

    # Loop through each CSV file in the current directory
    for filename in "${csv_files[@]}"; do
        # Append file name and the first row to the output file
        echo -e "\n$filename" >>"$output_file"
        head -n 1 "$filename" >>"$output_file"
        echo "First row of $filename has been appended to $output_file"
    done

    echo "All CSV files' first rows have been written to $output_file"
}

extract_and_clean_text_from_pdfs() {
    response=$(get_input_or_default "Enter the directory to start the recursive text extraction and cleaning. Press enter to start in the current directory.")
    echo -e "Extracting and cleaning text (recursively)\n$response"
    start_scripts_venv
    python _01c_extract_name_and_clean.py "$response"
    echo -e "Text extraction is complete."
}

summarize_and_tag_pdfs() {
    response=$(get_input_or_default "Enter the directory to start the summarization and tagging. Press enter to start in the current directory.")
    echo -e "Summarizing and tagging (recursively)\n$response"
    start_scripts_venv
    python _02b_summarize_and_tag_with_gemini.py $response
    echo -e "Summarization complete."
}

transcribe_new_voice_memos() {
    echo -e "Beginning conversion and transcription in ${VOICE_MEMO_FOLDER}"
    _04a_transcribe_folder_m4a_to_mp3_to_deep.sh "$VOICE_MEMO_FOLDER"
    echo -e "Transcription of voice memos is complete."
}

transcribe_named_folder() {
    response=$(get_input_or_default "Enter the directory with the audio recordings. Press enter to start in the current directory.")
    echo -e "Beginning conversion and transcription in $response"
    _04a_transcribe_folder_m4a_to_mp3_to_deep.sh $response
    echo -e "Transcription complete."
}

update_secrets_google_cloud() {
    start_scripts_venv
    python "${SCRIPT_PATH}/_100_update_secrets.py"
}

kill_process_by_name() {
    PROCESS_NAME=$1
    echo -e "Killing all ${PROCESS_NAME} processes..."
    pkill -f "${PROCESS_NAME}"
    sleep 1
    if pgrep -f "${PROCESS_NAME}" >/dev/null; then
        echo -e "Some ${PROCESS_NAME} processes could not be terminated. Retrying..."
        sleep 3
        pkill -f "${PROCESS_NAME}"
    fi
    echo -e "All ${PROCESS_NAME} processes terminated."
}

install_or_upgrade_cask() {
    if brew list --cask | grep -q "^$1\$"; then
        echo "Upgrading $1..."
        brew upgrade --cask $1
    else
        echo "Installing $1..."
        brew install --cask $1
    fi
}

get_input_or_default() {
    local prompt="$1"
    local default_value="${2:-$(pwd)}"
    read -p "${prompt}" user_input
    if [ -z "$user_input" ]; then
        echo "$default_value"
    else
        echo "$user_input"
    fi
}

stop_and_remove_container() {
    if docker ps -q -f name="$CONTAINER_NAME" >/dev/null; then
        echo "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
    fi
    if docker ps -aq -f name="$CONTAINER_NAME" >/dev/null; then
        echo "Removing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
    fi
}

pull_latest_image() {
    echo "Pulling the latest Docker image: $IMAGE_NAME"
    docker pull "$IMAGE_NAME"
}

run_container_openwebui() {
    docker run -d \
        -p 3000:8080 \
        --name "open-webui" \
        "${IMAGE_NAME}"
}

options=(
    "${OPTION00}" "${OPTION01}" "${OPTION02}" "${OPTION03}" "${OPTION04}" "${OPTION05}"
    "${OPTION06}" "${OPTION07}" "${OPTION08}" "${OPTION09}" "${OPTION10}" "${OPTION11}" "${OPTION12}"
)

# Main Menu Logic
select opt in "${options[@]}"; do
    case $opt in
    "${OPTION00}") commit_current_folder_menu ;;
    "${OPTION01}") extract_and_clean_text_menu ;;
    "${OPTION02}") summarize_text_menu ;;
    "${OPTION03}") transcribe_voicememos_menu ;;
    "${OPTION04}") transcribe_recordings_menu ;;
    "${OPTION05}") restart_ollama_menu ;;
    "${OPTION06}") kill_ollama_menu ;;
    "${OPTION07}") kill_python_menu ;;
    "${OPTION08}") restart_postgres_menu ;;
    "${OPTION09}") install_open_web_ui_menu ;;
    "${OPTION10}") set_ollama_env_menu ;;
    "${OPTION11}") update_google_secrets_menu ;;
    "${OPTION12}") restart_open_web_ui_menu ;;
    "${OPTION13}") extract_5_rows_csv_file_menu ;;
    "${OPTION14}") extract_1_row_csv_folder_menu ;;
    "Exit")
        echo -e "${GREEN}Exiting. Goodbye!${NC}"
        break
        ;;
    *)
        echo -e "${RED}Invalid option. Try again.${NC}"
        ;;
    esac
done
exit 0
