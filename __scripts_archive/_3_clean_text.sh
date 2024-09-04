#!/bin/bash




# Define the virtual environment and command to run in each subfolder
SCRIPTS="${HOME}/code/mytech/docker/Utils/scripts"
VENV_PATH="${SCRIPTS}/scripts_venv/bin/activate"
SCRIPT_PATH="${SCRIPTS}/_py3_clean_text.py"

# Check if the virtual environment exists
if [ ! -f "$VENV_PATH" ]; then
    echo "Virtual environment not found at $VENV_PATH"
    exit 1
fi


# Check if the first parameter is provided
if [ -n "$1" ]; then
    # If a parameter is provided, use it
    target_dir="$1"
else
    # If no parameter is provided, use the current working directory
    target_dir="$(pwd)"
fi



# Define the log file
log_file="${target_dir}/clean_text_log.txt"

# Function to run the command in a subfolder
run_command_in_subfolder() {
    subfolder="$1"
    (
        cd "$subfolder" || {
            echo "Failed to cd into $subfolder"
            exit 1
        }

        # Check each PDF file in the subfolder
        for pdf_file in *.pdf; do
            if [ -e "$pdf_file" ]; then
                base_name="${pdf_file%.pdf}"
                txt_file="${base_name}_raw_extract.txt"

                if [ -f "$txt_file" ]; then
                    echo "Processing $pdf_file in $subfolder" >>"$log_file"
                    source "${VENV_PATH}"
                    python3 "${SCRIPT_PATH}" "${pdf_file}" >>"${log_file}" 2>&1
                    if [ $? -ne 0 ]; then
                        echo "Command failed for $pdf_file in $subfolder" >>"$log_file"
                    fi
                    sleep 1
                else
                    echo "Skipping $pdf_file in $subfolder, $txt_file already exists" >>"$log_file"
                fi
            fi
        done
    )
}

# Export the function so it can be used by xargs
export -f run_command_in_subfolder
export VENV_PATH SCRIPT_PATH log_file

# Find all subdirectories recursively and run the command concurrently
find "$target_dir" -type d -print0 | xargs -0 -n 1 -I {} bash -c 'run_command_in_subfolder "$@"' _ "{}"

echo "All commands have been initiated. Check the log file at $log_file for details."
