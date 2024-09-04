#!/bin/bash

## Helper Function
ensure_process_running() {
    llm_script_path="$1"
    port="$2"
    llm_name="$3"

    # Check if process is already running on the specified port
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo -e "\033[1;95mProcess on port $port is already running. Killing it.\033[0m"
        kill -9 $(lsof -t -i:$port) # Forcefully kill the existing process
    fi

    if [ "$STOP_ONLY" -eq 1 ]; then
        return 0
    fi

    # Launch the process
    echo -e "\033[1;32mLaunching Chainlit for ${llm_name} chat via $llm_script_path on port $port\033[0m"
    chainlit run "$llm_script_path" --port "$port" --headless -w &

    # Wait for the process to start
    sleep 3

    # Check if the process is running now
    if [ $? -ne 0 ]; then
        echo -e "\033[1;31mFailed to launch Chainlit for ${llm_name} chat. Exiting.\033[0m"
        exit 1
    fi

}

function isStopParamAvailable() {
    if [ -z "$1" ]; then
        echo -e "\n\n"
        echo -e "\033[1;32m######################################################\033[0m"
        # echo -e "\033[1;32mNo 'Stop' parameter provided. Continue as planned with restart \033[0m"
        echo -e "\033[1;32mBeginning Shutdown and Restart of LLMs and Chat Interfaces\033[0m"
        STOP_ONLY=0

    else
        echo -e "\n\n"
        echo -e "\033[4;34m######################################################\033[0m"
        echo -e "\033[4;34mSTOP parameter received\033[0m"
        echo -e "\033[4;34mBeginning Shutdown of LLMs and Chat Interfaces\033[0m"
        STOP_ONLY=1

    fi
}

isStopParamAvailable "$1"

echo "Value of Stop only: $STOP_ONLY"

#These variables are set to allow this script to work if the project is moved to another location
CURRENT_DIR_NAME=$(basename "$PWD")
CURRENT_DIR_PATH=$(pwd)
echo -e "\nCurrent directory name: ${CURRENT_DIR_NAME}"
echo -e "Current directory path: ${CURRENT_DIR_PATH}"

# Activate the python virtual environment
VIRTUAL_ENV_ACTIVATION_PATH="${CURRENT_DIR_PATH}/${CURRENT_DIR_NAME}_venv/bin/activate"
echo "\nAttempting to activate the python virtual environment at ${VIRTUAL_ENV_ACTIVATION_PATH}"
source "${VIRTUAL_ENV_ACTIVATION_PATH}" || {
    echo -e "\033[1;31mActivating python virtual environment at ${VIRTUAL_ENV_ACTIVATION_PATH} failed. Exiting.\033[0m"
    exit 1
}
echo -e "\033[1;32mPython virtual environment activated successfully\033[0m"

echo -e "\n\033[1mProcessing Ollama Gemma 2B\033[0m"
ensure_process_running "${CURRENT_DIR_PATH}/llm/ollama-gemma2b.py" 5011 "Gemma 2B"

echo -e "\n\033[1mProcessing Ollama Gemma 7B\033[0m"
ensure_process_running "${CURRENT_DIR_PATH}/llm/ollama-gemma7b.py" 5012 "Gemma 7B"

echo -e "\n\033[1mProcessing Ollama Mistral 7B\033[0m"
ensure_process_running "${CURRENT_DIR_PATH}/llm/ollama-mistral7b.py" 5013 "Mistral 7B"

echo -e "\n"
echo -e "#############################################################"
if [ "$STOP_ONLY" -eq 1 ]; then
    echo -e "\033[5;91m#########   All LLMs and Chat Interfaces STOPPED.   #########\033[0m"

else
    echo -e "\033[4;32m##   All LLMs and Chat Interfaces LAUNCHED SUCCESSFULLY.   ##\033[0m"

fi
echo -e "#############################################################"
exit 0
