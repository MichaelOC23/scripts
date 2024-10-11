#!/bin/bash
# ENV_VARIABLES.sh

#Key Assumptions (that can be unique to the machine)
PYTHON_CLASSES_FOLDER_PATH="${HOME}/code/scripts/classes"
export PYTHONPATH="${PYTHON_CLASSES_FOLDER_PATH}"
# PYTHON_CLASSES_FOLDER_PATH="${HOME}/code/scripts"

export STREAMLIT_PRIMARY_COLOR="#98CCD0"
export STREAMLIT_BACKGROUND_COLOR="#003366"
export STREAMLIT_SECONDARY_BACKGROUND_COLOR="#404040"
export STREAMLIT_TEXT_COLOR="#CBD9DF"

export STREAMLIT_DEV_MODE="TRUE"

# Key Communify Locations
export PLATFORM_PATH="${HOME}/code/platform"
export PLATFORM_API_PATH="${HOME}/code/platform/Src/Api"
export PLATFORM_PROJECT="${PLATFORM_PATH}/Src/Api/Api.csproj"
export FRONTEND_PATH="${HOME}/code/frontend"
export SCRIPTS_PATH="${HOME}/code/scripts"
export SCRIPTS_LIVE_PATH="${HOME}/code/scripts/_live"
export NOTES_PATH="${HOME}/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/Notes\ by\ Michael"
export GOOGLE_CLOUD_FIREBASE_KEY="/Users/michasmi/.setup/keys/toolsexplorationfirebase-5f4d4c4c883e.json"

LLM_DATA="${HOME}/data-llm"
OLLAMA_DATA="${LLM_DATA}/ollama-data"
OLLAMA_TEMP="${LLM_DATA}/temp"
mkdir -p "${OLLAMA_TEMP}"

export OLLAMA_HOME="${OLLAMA_DATA}"
# export OLLAMA_LLM_LIBRARY="${OLLAMA_DATA}/library" (N/A for Macs)
export OLLAMA_MODELS="${OLLAMA_DATA}/models"
export OLLAMA_CACHE_DIR="${OLLAMA_DATA}/cache"
export OLLAMA_TMPDIR="${OLLAMA_TEMP}"

#Key Folder Locations for python scripts and projects
export NVM_DIR="/opt/homebrew/Cellar/nvm/0.39.7"

# PATH export (Standard mac path)
export PATH="/System/Cryptexes/App/usr/bin:/usr/bin:/bin" # Standard Path
export PATH="${PATH}:/usr/sbin:/sbin:/usr/local/bin"      # Standard Path

# Add additional locations to the PATH
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH" # Homebrew (prioritizing it over the system python)
export PATH="${PATH}:${HOME}/code/scripts"               # personal scripts
export PATH="${PATH}:/Applications/geckodriver*"
export PATH="${PATH}:${SCRIPTS_LIVE_PATH}:${SCRIPTS_PATH}"

export PGPORT=4999s


ollama serve &