import pandas as pd
from ics import Calendar, Event
from datetime import datetime, timedelta

def create_ics_from_xlsx(xlsx_path, output_ics_path):
    # Load the Excel file
    df = pd.read_excel(xlsx_path)

    # Initialize a calendar
    calendar = Calendar()

    # Loop through each event in the DataFrame
    for index, row in df.iterrows():
        # Create a new ICS event
        event = Event()

        # Parse event name
        event.name = row['Event']

        # Handle date formats and missing values
        start_date_str = row['Event Start Date']
        end_date_str = row['End Date']
        begin_time_str = row['Begin Time']
        end_time_str = row['End Time']
        event_type = row['Event Type']

        # Convert date to YYYY-MM-DD format for ICS
        if pd.notna(start_date_str):
            start_date = datetime.strptime(start_date_str, '%m/%d/%y')
        else:
            continue  # Skip if no start date

        if pd.notna(end_date_str):
            end_date = datetime.strptime(end_date_str, '%m/%d/%y')
        else:
            end_date = start_date  # Default to start date if no end date

        # Handle all-day events
        if event_type == 'All Day Event':
            event.begin = start_date.date()  # Only date, no time
            event.end = end_date.date() + timedelta(days=1)  # All-day events are exclusive of end date
        else:
            # Handle time format conversion for regular events
            if pd.notna(begin_time_str):
                begin_time = datetime.strptime(begin_time_str, '%I:%M %p').time()
                event.begin = datetime.combine(start_date, begin_time)
            else:
                event.begin = start_date

            if pd.notna(end_time_str):
                end_time = datetime.strptime(end_time_str, '%I:%M %p').time()
                event.end = datetime.combine(end_date, end_time)
            else:
                event.end = event.begin + timedelta(hours=1)  # Default to a 1-hour event if no end time provided

        # Handle multi-day events by setting the end date
        if 'Multi Day Event' in event_type:
            event.end = end_date + timedelta(days=1)

        # Add the event to the calendar
        calendar.events.add(event)

    # Write to an ICS file
    with open(output_ics_path, 'w') as f:
        f.writelines(calendar.serialize_iter())

    print(f"ICS file created: {output_ics_path}")

# Example usage
xlsx_path = './calendar_events/calendar_events.xlsx'  # Replace with your CSV file path
output_ics_path = 'outlook_events.ics'  # Specify the output ICS file path
create_ics_from_xlsx(xlsx_path, output_ics_path)