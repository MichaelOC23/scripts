#!/bin/bash

ensure_process_stopped_by_name() {
    process_name="$1"

    # Get PIDs of processes with names containing the provided pattern
    pids=$(pgrep -f "$process_name")

    if [ -n "$pids" ]; then # If any PIDs were found
        echo -e "\033[1;95m ** ${process_name} processes are running. Killing them:\033[0m **"
        echo "$pids" # Display the PIDs for clarity

        kill -9 $pids                                  # Forcefully kill the processes
        ensure_process_stopped_by_name ${process_name} # Call the function again to ensure the processes were killed
    else
        echo -e "\033[1;92mNo ${process_name} processes found running.\033[0m"
    fi
}

# Call the function to kill processes with 'docker' in their names
ensure_process_stopped_by_name "MyTechFlaskBackground"

# Change to the directory where the code is located
cd /Users/michasmi/code/MyTech
echo "Changed to the directory where the code is located."

# Activate the virtual environment and set the FLASK_APP environment variable
source /Users/michasmi/code/MyTech/venv/bin/activate
echo "Activated the virtual environment."

# Set the FLASK_APP environment variable (which is the path to the Flask app)
export FLASK_APP=/Users/michasmi/code/MyTech/FlaskBackground.py

# Run the Flask app in the background
cd /Users/michasmi/code/MyTech/classes
python FlaskBackground.py

# flask run --port 5005 &
echo "Flask app running in the background."

# Wait before resuming the script
echo "Waiting for 5 seconds to test the app."
sleep 5 # Pause for 5 seconds
curl http://127.0.0.1:5005/isup
