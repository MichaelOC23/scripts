#!/bin/bash
# ENV_VARIABLES.sh

#Key Assumptions (that can be unique to the machine)
PYTHON_CLASSES_FOLDER_PATH="${HOME}/code/scripts/classes"
export PYTHONPATH="${PYTHON_CLASSES_FOLDER_PATH}"
# PYTHON_CLASSES_FOLDER_PATH="${HOME}/code/scripts"

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

# Capture and print the current time:
ENV_VAR_LOAD_DATE_TIME=$(date '+%Y-%m-%d %H:%M:%S')
export ENV_VAR_LOAD_DATE_TIME
export PGPORT=4999

# Run commands for the platform and frontend for Communify
alias run_frontend='(cd "${FRONTEND_PATH}" && npm i && npm start)'
alias run_platform='(cd "${PLATFORM_API_PATH}" && dotnet build -c Debug && dotnet run)'
alias add_spacer="defaults write com.apple.dock persistent-apps -array-add '{\"tile-type\"=\"small-spacer-tile\";}'; killall Dock"
alias source_env='(source ~/code/scripts/env_variables.sh)'
alias source_scripts="source /Users/michasmi/code/scripts/scripts_venv/bin/activate "
alias run_openwebui='docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main'
CDS="cd ${SCRIPTS_PATH}"
alias cd_scripts="${CDS}"
CDN="cd ${NOTES_PATH}"
alias cd_notes="${CDN}"
alias start_docker="docker run --name my_postgres_container \
  -e ALLOW_EMPTY_PASSWORD=yes \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_DB=postgres \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -v ~/code/postgres:/var/lib/postgresql/data \
  -p 5454:5432 \
  -d postgres"

#Standardize python commands
alias python='python3'
alias pip='pip3'
# alias extract_text="source ${HOME}/code/scripts/scripts_venv/bin/activate && python3 ${HOME}/code/scripts/extract_text_from_folder_recursively.py "
# alias summarize_text="source ${HOME}/code/scripts/scripts_venv/bin/activate && python3 ${HOME}/code/scripts/summarize_recursively.py "

# Set the default editor to Visual Studio Code
export EDITOR="code"

#Streamlit
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10000

# export STREAMLIT_PRIMARYCOLOR="#006629" #003366
# export STREAMLIT_BACKGROUNDCOLOR="#FFFFFF"
# export STREAMLIT_SECONDARYBACKGROUNDCOLOR="#EFF7FF"
# export STREAMLIT_TEXTCOLOR="#000000"
# export STREAMLIT_FONT="sans serif"
# export STREAMLIT_BASE="light"

# Transcriptions
export OPENAI_TRANSCRIPTION_ENDPOINT="https://api.openai.com/v1/transcriptions"
export TRANSCRIPTION_BASE_DIR="/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes by Michael/Transcriptions"

#JBI/NG Application
export NG_CODE_DIR="${HOME}/code"
export NG_PLATFORM_DIR="${NG_CODE_DIR}/platform"
export NG_API_DIR="${NG_PLATFORM_DIR}/Src/Api"

# # Ensure the provided path is a directory
# if [ ! -d "$PYTHON_CLASSES_FOLDER_PATH" ]; then
#     echo -e "${RED_U}Error: The path for Python Classes [$PYTHON_CLASSES_FOLDER_PATH] is not a valid path.${NC}"
#     echo -e "${RED_U}Python classes were not exported to the PYTHONPATH.${NC}"
# else
#     echo -e "${GREEN}Python classes folder: [${PYTHON_CLASSES_FOLDER_PATH}] .${NC}"
#     for FILE in "$PYTHON_CLASSES_FOLDER_PATH"/*.py; do
#         if [ -f "$FILE" ]; then
#             export PYTHONPATH="${PYTHONPATH}:${FILE}"
#             # echo -e "${GREEN}Added Python file to PYTHONPATH: \n[${PYTHONPATH}]${NC}\n"
#         fi
#     done
# fi

#Color Variables for text
export BLACK='\033[0;30m'
export RED='\033[0;31m'
export RED_U='\033[4;31m'
export RED_BLINK='\033[5;31m'
export GREEN='\033[0;32m'
export GREEN_BLINK='\033[5;32m'
export YELLOW='\033[0;33m'
export YELLOW_BOLD='\033[1;33m'
export PURPLE='\033[1;34m'
export PURPLE_U='\033[4;34m'
export PURPLE_BLINK='\033[5;34m'
export PINK='\033[0;35m'
export PINK_U='\033[4;35m'
export PINK_BLINK='\033[5;35m'
export LIGHTBLUE='\033[0;36m'
export LIGHTBLUE_BOLD='\033[1;36m'
export GRAY='\033[0;37m'
export ORANGE='\033[1;91m'
export BLUE='\033[1;94m'
export CYAN='\033[1;96m'
export WHITE='\033[1;97m'
export MAGENTA='\033[1;95m'
export BOLD='\033[1m'
export UNDERLINE='\033[4m'
export BLINK='\033[5m'
export NC='\033[0m' # No Color

# Sync with the Dashlane CLI. This updates the secrets to be stored locally
dcli sync

# Get all the locally stored secrets
json_string=$(dcli note localeFormat=UNIVERSAL -o json)
env_vars=""
echo -e "${LIGHTBLUE_BOLD}-> Secrets: \033[0;32mSuccessfully updated ${NC}"
# echo -e "$json_string" > delete-me.json # Save the JSON to a file for debugging

# Loop through each entry in the JSON array
echo "$json_string" | jq -c '.[]' | while read -r I; do
  # Extract title and content
  title=$(echo "$I" | jq -r '.title')
  content=$(echo "$I" | jq -r '.content')

  # Construct the export statement correctly
  env_vars="${env_vars}export ${title}=\"${content}\"\n"

  # Append to SECRET_TITLES
  SECRET_TITLES="${SECRET_TITLES}\n${title}=${content}"
done

# Correctly evaluate the environment variables
echo -e "$env_vars" | while read -r line; do
  eval "$line"
done

##### NGROK#####
# Get the ngrok public URL
# Make the curl request and use jq to parse the JSON response, extracting the public_url
# NGROK_PUBLIC_URL=$(curl -s \
#     -X GET \
#     -H "Authorization: Bearer ${NGROK_API_KEY}" \
#     -H "Ngrok-Version: 2" \
#     "https://api.ngrok.com/endpoints" | jq -r '.endpoints[0].public_url')
# Export the public URL as an environment variable
# echo "Extracted Public URL: $NGROK_PUBLIC_URL"
# export NGROK_PUBLIC_URL

# Now, NGROK_PUBLIC_URL is available as an environment variable in this script's execution context
# To use it in other terminal sessions or scripts, you might need to source this script or handle it differently

# op read op://app-prod/db/password
