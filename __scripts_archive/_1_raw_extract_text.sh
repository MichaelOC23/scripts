#!/bin/bash

# Define the virtual environment and command to run in each subfolder
VENV_PATH="${HOME}/code/mytech/docker/Utils/scripts/scripts_venv/bin/activate"
SCRIPT_PATH="${HOME}/code/mytech/docker/Utils/scripts/_py1_extract_text_from_scan_pdf.py"

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

echo -e "Target directory: ${target_dir}\033[0m"

# Define the log file
log_file="${target_dir}/ext_text_parallel.md"

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

                if [ ! -f "$txt_file" ]; then
                    echo "Processing $pdf_file in $subfolder" >>"$log_file"
                    source "$VENV_PATH"
                    python3 "$SCRIPT_PATH" "$pdf_file" >>"$log_file" 2>&1 &
                    if [ $? -ne 0 ]; then
                        echo "Command failed for $pdf_file in $subfolder" >>"$log_file"
                    fi
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

# Find all subdirectories and run the command concurrently
find "$target_dir" -mindepth 1 -maxdepth 1 -type d -print0 | xargs -0 -n 1 -P 0 -I {} bash -c 'run_command_in_subfolder "$@"' _ "{}"

echo "All commands have been initiated. Check the log file at $log_file for details."
