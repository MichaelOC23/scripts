



import csv

from datetime import datetime

# Define the input and output file names
input_file = 'data/nasdaq/DAILY.csv'
output_file = 'data/nasdaq/filtered_daily.csv'

# Define the cutoff date
cutoff_date = datetime.strptime('2016-12-31', '%Y-%m-%d')

# Open the input CSV file
with open(input_file, mode='r', newline='') as infile:
    reader = csv.reader(infile)
    header = next(reader)  # Read the header row
    
    # Open the output CSV file
    with open(output_file, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)  # Write the header row to the output file
        
        # Process each row in the input file
        for row in reader:
            date_str = row[1]  # Get the date from the second column
            try:
                # Convert the date string to a datetime object
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                # Check if the date is after the cutoff date
                if date_obj > cutoff_date:
                    writer.writerow(row)  # Write the row to the output file if the date is after the cutoff date
            except ValueError:
                # If the date string is not in the correct format, skip the row
                print(f"Skipping row with invalid date format: {row}")
