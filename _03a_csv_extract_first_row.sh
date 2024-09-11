#!/bin/bash

# Check if there are any CSV files in the current directory
shopt -s nullglob
csv_files=(*.csv)

if [ ${#csv_files[@]} -eq 0 ]; then
    echo "No CSV files found in the current directory."
    exit 1
fi

# Output file name where all data will be concatenated
output_file="combined_output.txt"

# Create or overwrite the output file
: >"$output_file"

# Loop through each CSV file in the current directory
for filename in "${csv_files[@]}"; do
    # Append file name and the first row to the output file
    echo -e "\n$filename" >>"$output_file"
    head -n 1 "$filename" >>"$output_file"
    echo "First row of $filename has been appended to $output_file"
done

echo "All CSV files' first rows have been written to $output_file"
