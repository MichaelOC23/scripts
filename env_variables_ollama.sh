#!/bin/bash

# Define the plist file path and label (the label used in the plist)
PLIST_FILE="${HOME}/Library/LaunchAgents/ai-environment.plist"
LABEL="set-ai-env-vars"

# Check if the service is already loaded
if launchctl list | grep -q "$LABEL"; then
    echo "Service is loaded. Unloading..."
    launchctl unload "$PLIST_FILE"
    rm -rf "$PLIST_FILE"
else
    echo "Service is not loaded."
fi

# Create the directory if it doesn't exist
mkdir -p "$(dirname "$PLIST_FILE")"

# Write the XML content to the plist file
cat <<EOL >"$PLIST_FILE"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>set-ai-env-vars</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>bash</string>
        <string>-c</string>
        <string>
            export LLM_DATA="\${HOME}/data-llm" &&
            export OLLAMA_DATA="\${LLM_DATA}/ollama-data" &&
            export OLLAMA_TEMP="\${LLM_DATA}/temp" &&
            export OLLAMA_HOME="\${OLLAMA_DATA}" &&
            export OLLAMA_MODELS="\${OLLAMA_DATA}/models" &&
            export OLLAMA_CACHE_DIR="\${OLLAMA_DATA}/cache" &&
            export OLLAMA_TMPDIR="\${OLLAMA_TEMP}" &&
            export OLLAMA_HOST="0.0.0.0" &&
            export STREAMLIT_BROWSER_SERVERADDRESS="localhost" &&
            export STREAMLIT_BROWSER_GATHERUSAGESTATS=false &&
            export STREAMLIT_SERVER_FOLDERWATCHBLACKLIST="[]" &&
            export STREAMLIT_SERVER_HEADLESS=true &&
            export STREAMLIT_SERVER_RUNONSAVE=true &&
            export STREAMLIT_SERVER_PORT=5010 &&
            export STREAMLIT_SERVER_ENABLECORS=false &&
            export STREAMLIT_SERVER_ENABLEXSRFPROTECTION=true &&
            export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=10000 &&
            export STREAMLIT_SERVER_MAXMESSAGESIZE=10000 &&
            export STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION=false &&
            export STREAMLIT_SERVER_ENABLESTATICSERVING=false &&
            export STREAMLIT_RUNNER_MAGICENABLED=false &&
            export STREAMLIT_RUNNER_FASTRERUNS=true &&
            export STREAMLIT_RUNNER_ENFORCESERIALIZABLESESSIONSTATE=false &&
            export STREAMLIT_RUNNER_ENUMCOERCION="nameOnly"
        </string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOL
chmod 644 "$PLIST_FILE"

# Load the plist with launchctl
launchctl load "$PLIST_FILE"

echo "Environment variables have been set and loaded successfully."
