# #!/bin/bash
# # ENV_VARIABLES.sh

source "${HOME}/.config/secrets.sh"

export TEST_AUDIO="\"/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/_AudioRecordings/20240712 100916-4B0A23BA.m4a\""

export SCRIPTS_PATH="${HOME}/code/scripts"
export SCRIPTS_LIVE_PATH="${HOME}/code/scripts/_live"

# SCRIPTS_CLASSES_FOLDER_PATH="${HOME}/code/scripts/classes"
GCLOUD_CLASSES_FOLDER_PATH="${HOME}/code/gcloud/gcloud-classes"
export PYTHONPATH="${PYTHONPATH}:${GCLOUD_CLASSES_FOLDER_PATH}"

export GOOGLE_CLOUD_FIREBASE_KEY="/Users/michasmi/.config/toolsexplorationfirebase-5f4d4c4c883e.json"
# export COMMUNIFY_HORIZONS_OAUTH_2_CREDENTIAL=$(cat "${HOME}/.config/client_secret_236139179984-damhhom05d0bl3d59qfgnova76eadlbh.apps.googleusercontent.com.json")

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
alias source_scripts="source /Users/michasmi/code/scripts/scripts_venv/bin/activate "
alias run_openwebui='docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main'
alias cd_scripts='cd ${SCRIPTS_PATH}'
# alias horizon_quart_test="curl -F "file=@${test_audio_file_path}" -H "x-api-key: your_correct_api_key" http://yourserver:4001/uploadfile"
alias python='python3'
alias pip='pip3'

#Standardize python commands
# alias extract_text="source ${HOME}/code/scripts/scripts_venv/bin/activate && python3 ${HOME}/code/scripts/extract_text_from_folder_recursively.py "
# alias summarize_text="source ${HOME}/code/scripts/scripts_venv/bin/activate && python3 ${HOME}/code/scripts/summarize_recursively.py "

# Set the default editor to Visual Studio Code
export EDITOR="code"

#Key Folder Locations for python scripts and projects
export NVM_DIR="/opt/homebrew/Cellar/nvm/0.39.7"

source streamlit_theme.sh
