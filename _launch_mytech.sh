#!/bin/bash

ensure_process_stopped() {
    port="$1"
    # Check if process is already running on the specified port
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo -e "\033[1;95mProcess on port $port is already running. Killing it.\033[0m"
        kill -9 $(lsof -t -i:$port) # Forcefully kill the existing process
    fi
}


# Ensure that the processes are stopped
ensure_process_stopped 2000 # Streamlit
# ensure_process_stopped 5005 # Dow Jones Service

if [ "$STOP_ONLY" -eq 1 ]; then
    echo -e "\033[4;34mAll Services Stopped\033[0m"
    exit
fi

# Change to the directory where the code is located
cd ~/code/mytech

# Activate the virtual environment
# source ~/code/dow_jones_service/dow_jones_service_venv/bin/activate

# # Set the environment variables
# export FLASK_APP=_flask_dow_jones.py
# export FLASK_ENV=development
# export FLASK_DEBUG=1

# # Specify a custom port for Flask and make server externally visible
# export FLASK_RUN_PORT=5005
# export FLASK_RUN_HOST=0.0.0.0

# # Run the Flask application in the background
# flask run --host=0.0.0.0 --port 5005 &

# Run the Streamlit application in the foreground
source /Users/michasmi/code/mytech/mytech_venv/bin/activate && streamlit run 000_Meeting_Tech.py --server.address 0.0.0.0 --server.port 2000

# Activate the virtual environment
# source /Users/michasmi/code/mytech/mytech_venv/bin/activate

# Run the Streamlit application in the foreground
# python _class_dow_jones.py
