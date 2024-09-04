#!/bin/bash



#!/bin/bash

# Get the current working directory
current_dir=$(pwd)

# Extract the parent directory name
parent_dir_name=$(basename "$current_dir")

# Get current date and time in YYYYMMDD_HHMMSS format
current_date=$(date +%Y%m%d_%H%M%S)

# Define the filename as the parent directory name followed by the current date and time
output_file="file_structure_${parent_dir_name}_${current_date}.txt"


# Write header to the output file
echo "Size | Type | Name | Path" >$output_file

# Function to process files
process_files() {
    local dir=$1
    for file in "$dir"/*; do
        if [ -d "$file" ]; then
            # If it's a directory, recurse into it
            process_files "$file"
        elif [ -f "$file" ]; then
            # If it's a file, process it
            filename=$(basename "$file")
            filetype=$(file --brief --mime-type "$file" | awk -F'/' '{print toupper($2)}')
            [ -z "$filetype" ] && filetype="Unknown"
            fullpath=$(realpath "$file")
            filesize=$(stat -f%z "$file")

            # Append information to the output file
            echo "$filesize | $filetype | \"$filename\" | \"$fullpath\"" >>$output_file
        fi
    done
}

# Start processing from the current directory
process_files "$current_dir"
