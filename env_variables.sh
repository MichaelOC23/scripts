# #!/bin/bash
# # ENV_VARIABLES.sh

source "${HOME}/.config/secrets.sh"

# enable homebrew installation
eval "$(/opt/homebrew/bin/brew shellenv)"

# updates dashlane
dcli sync

export TEST_AUDIO="\"/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/_AudioRecordings/20240712 100916-4B0A23BA.m4a\""

export SCRIPTS_PATH="${HOME}/code/scripts"
export SCRIPTS_LIVE_PATH="${HOME}/code/scripts/_live"

GCLOUD_CLASSES_FOLDER_PATH="${HOME}/code/gcloud/gcloud-classes"
export PYTHONPATH="${PYTHONPATH}:${GCLOUD_CLASSES_FOLDER_PATH}"

# Google Cloud Configuration Keys
export GOOGLE_APPLICATION_CREDENTIALS="${HOME}/.config/google-cloud-toolsexplorationfirebase.json"
export PROJECT_ID="toolsexplorationfirebase" #For Firebase
export GCLOUD_PROJECT="toolsexplorationfirebase" #Fort the rest of google cloud
export GOOGLE_CLOUD_PROJECT="toolsexplorationfirebase" #Fort the rest of google cloud
export FIREBASE_STORAGE_BUCKET="toolsexplorationfirebase.appspot.com"

# Preferred Ollama Models
export OLLAMA_BEST_EMBEDDINGS='mxbai-embed-large'
export OLLAMA_BEST_LANGUAGE='phi3.5:latest'
export OLLAMA_BEST_REASONING='llama3.1:8b'

# PATH export (Standard mac path)
export PATH="/System/Cryptexes/App/usr/bin:/usr/bin:/bin" # Standard Path
export PATH="${PATH}:/usr/sbin:/sbin:/usr/local/bin"      # Standard Path

# Add additional locations to the PATH
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:$PATH" # Homebrew (prioritizing it over the system python)
export PATH="${PATH}:${HOME}/code/scripts"               # personal scripts
export PATH="${PATH}:/Applications/geckodriver*"
export PATH="${PATH}:${SCRIPTS_LIVE_PATH}:${SCRIPTS_PATH}"

alias add_spacer="defaults write com.apple.dock persistent-apps -array-add '{\"tile-type\"=\"small-spacer-tile\";}' && killall Dock"
alias source_env='(source ~/code/scripts/env_variables.sh)'

alias run_horizons='source /Users/michasmi/code/horizons/horizons_venv/bin/activate && cd /Users/michasmi/code/horizons && export LOCAL_STREAMLIT_PORT=5012 && streamlit run app.py --server.port "${LOCAL_STREAMLIT_PORT}" && open "http://localhost:${LOCAL_STREAMLIT_PORT}"'
alias source_scripts="source /Users/michasmi/code/scripts/scripts_venv/bin/activate "

alias cd_horizons='cd /Users/michasmi/code/horizons && source /Users/michasmi/code/horizons/horizons_venv/bin/activate '
alias cd_scripts='cd ${SCRIPTS_PATH}'

alias python='python3'
alias pip='pip3'

# Set the default editor to Visual Studio Code
export EDITOR="code"

#Key Folder Locations for python scripts and projects
export NVM_DIR="/opt/homebrew/Cellar/nvm/0.39.7"

source env_streamlit_theme.sh
source env_start_ollama.sh

# export STREAMLIT_CUSTOM_THEME="--theme.primaryColor #98CCD0 --theme.backgroundColor  #003366 --theme.secondaryBackgroundColor  #404040 --theme.textColor  #CBD9DF"