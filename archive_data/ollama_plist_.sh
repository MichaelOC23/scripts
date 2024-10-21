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
    <key>EnvironmentVariables</key>
    <dict>
        <key>LLM_DATA</key>
        <string>/Users/michasmi/data-llm</string>
        <key>OLLAMA_DATA</key>
        <string>/Users/michasmi/data-llm/ollama-data</string>
        <key>OLLAMA_TEMP</key>
        <string>/Users/michasmi/data-llm/temp</string>
        <key>OLLAMA_HOME</key>
        <string>/Users/michasmi/data-llm/ollama-data</string>
        <key>OLLAMA_MODELS</key>
        <string>/Users/michasmi/data-llm/ollama-data/models</string>
        <key>OLLAMA_CACHE_DIR</key>
        <string>/Users/michasmi/data-llm/ollama-data/cache</string>
        <key>OLLAMA_TMPDIR</key>
        <string>/Users/michasmi/data-llm/temp</string>
        <key>OLLAMA_HOST</key>
        <string>0.0.0.0</string>
        <key>STREAMLIT_BROWSER_SERVERADDRESS</key>
        <string>localhost</string>
        <key>STREAMLIT_BROWSER_GATHERUSAGESTATS</key>
        <false/>
        <key>STREAMLIT_SERVER_FOLDERWATCHBLACKLIST</key>
        <string>[]</string>
        <key>STREAMLIT_SERVER_HEADLESS</key>
        <true/>
        <key>STREAMLIT_SERVER_RUNONSAVE</key>
        <true/>
        <key>STREAMLIT_SERVER_PORT</key>
        <integer>5010</integer>
        <key>STREAMLIT_SERVER_ENABLECORS</key>
        <false/>
        <key>STREAMLIT_SERVER_ENABLEXSRFPROTECTION</key>
        <true/>
        <key>STREAMLIT_SERVER_MAX_UPLOAD_SIZE</key>
        <integer>10000</integer>
        <key>STREAMLIT_SERVER_MAXMESSAGESIZE</key>
        <integer>10000</integer>
        <key>STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION</key>
        <false/>
        <key>STREAMLIT_SERVER_ENABLESTATICSERVING</key>
        <false/>
        <key>STREAMLIT_RUNNER_MAGICENABLED</key>
        <false/>
        <key>STREAMLIT_RUNNER_FASTRERUNS</key>
        <true/>
        <key>STREAMLIT_RUNNER_ENFORCESERIALIZABLESESSIONSTATE</key>
        <false/>
        <key>STREAMLIT_RUNNER_ENUMCOERCION</key>
        <string>nameOnly</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOL

# Set correct permissions for the plist file
chmod 600 "$PLIST_FILE"

# Load the plist with launchctl
launchctl load "$PLIST_FILE"

echo "Environment variables have been set and loaded successfully."
