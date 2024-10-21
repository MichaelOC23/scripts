#!/bin/bash

# Function to kill the running Ollama process
kill_ollama() {
    if pgrep -x "ollama" >/dev/null; then
        echo -e "\033[1;33mRestart parameter detected. Killing existing Ollama process...\033[0m"
        pkill -x "ollama"
        sleep 2 # Give it time to shut down
    fi
}

# Check if the 'restart' parameter is passed
if [[ "$1" == "restart" ]]; then
    kill_ollama
fi

# Check if Ollama is already running
if pgrep -x "ollama" >/dev/null; then
    echo -e "\033[1;32mOllama is running.\033[0m"
else
    echo -e "\033[1;34mOllama is not running. Starting ollama serve...\033[0m"

    # Safely create data-llm folder
    LLM_DATA="${HOME}/data-llm"
    mkdir -p "${LLM_DATA}"

    # Safely create temp folder
    OLLAMA_TEMP="${LLM_DATA}/temp"
    mkdir -p "${OLLAMA_TEMP}"

    # Safely create ollama-data folder
    OLLAMA_DATA="${LLM_DATA}/ollama-data"
    mkdir -p "${OLLAMA_DATA}"

    # Export paths as env variables for ollama to utilize
    export OLLAMA_TMPDIR="${OLLAMA_TEMP}"
    export OLLAMA_HOME="${OLLAMA_DATA}"
    export OLLAMA_MODELS="${OLLAMA_DATA}/models"
    export OLLAMA_CACHE_DIR="${OLLAMA_DATA}/cache"

    # Start ollama and redirect output to a log file
    ollama serve >"${LLM_DATA}/ollama.log" 2>&1 &

    # Wait for start to complete
    sleep 2

    if [ $? -eq 0 ]; then
        echo -e "\033[1;32mOllama started successfully. Logs can be found at ${LLM_DATA}/ollama.log\033[0m"
    else
        echo -e "\033[1;31mFailed to start Ollama.\033[0m"
    fi
fi
