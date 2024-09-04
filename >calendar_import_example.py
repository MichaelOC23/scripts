from datetime import datetime, timedelta
import pytz

# Define events
events = [
    {"summary": "Back-to-School Social (Park Century)", "start": "2024-09-03 10:00", "end": "2024-09-03 14:00"},
    {"summary": "First Day of School (Minimum Day) (Park Century)", "start": "2024-09-04 08:45", "end": "2024-09-04 15:15"},
    {"summary": "Back-to-School BBQ (Park Century)", "start": "2024-09-21 17:00", "end": "2024-09-21 19:00"},
    {"summary": "Minimum Day / MS Back-to-School Night (Park Century)", "start": "2024-09-25 12:00", "end": "2024-09-25 20:00"},
    {"summary": "Minimum Day / LS Back-to-School Night (Park Century)", "start": "2024-10-09 12:00", "end": "2024-10-09 20:00"},
    {"summary": "Faculty Professional Development (Park Century)", "start": "2024-11-08 00:00", "end": "2024-11-08 23:59"},
    {"summary": "Faculty Professional Development (Park Century)", "start": "2024-11-11 00:00", "end": "2024-11-11 23:59"},
    {"summary": "Parent Association Gratitude Celebration (Park Century)", "start": "2024-11-22 12:00", "end": "2024-11-22 15:00"},
    {"summary": "Parent Conferences (Park Century)", "start": "2024-12-12 00:00", "end": "2024-12-13 23:59"},
    {"summary": "Fine Arts Showcase / Minimum Day (Park Century)", "start": "2024-12-18 12:00", "end": "2024-12-18 15:00"},
    {"summary": "Faculty Professional Development (Park Century)", "start": "2025-01-06 00:00", "end": "2025-01-06 23:59"},
    {"summary": "Classes Resume (Park Century)", "start": "2025-01-07 08:00", "end": "2025-01-07 17:00"},
    {"summary": "Grandparents and Special Friends Day / Minimum Day (Park Century)", "start": "2025-03-21 09:30", "end": "2025-03-21 15:00"},
    {"summary": "Faculty Professional Development (Park Century)", "start": "2025-04-07 00:00", "end": "2025-04-07 23:59"},
    {"summary": "Faculty Professional Development (Park Century)", "start": "2025-05-05 00:00", "end": "2025-05-05 23:59"},
    {"summary": "Teacher Appreciation Lunch / Minimum Day (Park Century)", "start": "2025-05-09 12:00", "end": "2025-05-09 15:00"},
    {"summary": "Minimum Day (Park Century)", "start": "2025-05-23 12:00", "end": "2025-05-23 15:00"},
    {"summary": "Parent Conferences (Park Century)", "start": "2025-05-29 00:00", "end": "2025-05-30 23:59"},
    {"summary": "Last Day of School / Field Day (Park Century)", "start": "2025-06-04 08:00", "end": "2025-06-04 15:00"},
    {"summary": "Classroom Parties (Park Century)", "start": "2025-06-05 08:00", "end": "2025-06-05 17:00"},
    {"summary": "8th Grade Graduation (Park Century)", "start": "2025-06-06 08:00", "end": "2025-06-06 17:00"},
    {"summary": "Early Dismissal (Park Century)", "start": "2024-09-20 14:00", "end": "2024-09-20 14:30"},
    {"summary": "Early Dismissal (Park Century)", "start": "2024-10-18 14:00", "end": "2024-10-18 14:30"},
    {"summary": "Early Dismissal (Park Century)", "start": "2025-01-31 14:00", "end": "2025-01-31 14:30"},
    {"summary": "Early Dismissal (Park Century)", "start": "2025-02-28 14:00", "end": "2025-02-28 14:30"},
    {"summary": "Early Dismissal (Park Century)", "start": "2025-04-25 14:00", "end": "2025-04-25 14:30"},
]

import ics
from ics import Calendar, Event

# Create a calendar
cal = Calendar()
timezone = pytz.timezone("America/Los_Angeles")

# Generate a random 5-digit number for the UID
import random
random.seed(0)
for event_data in events:
    event_data["uid"] = 

# Add events to calendar
for event_data in events:
    event = Event()
    event.name = event_data["summary"]
    event.begin = timezone.localize(datetime.strptime(event_data["start"], "%Y-%m-%d %H:%M"))
    event.end = timezone.localize(datetime.strptime(event_data["end"], "%Y-%m-%d %H:%M"))

    event.description = event_data.get("description", "")
    event.location = event_data.get("Park Century School", "")
    event.categories = set(['Personal', 'Park Century'])
    event.alarms = [ics.Alarm(trigger=timedelta(minutes=-30))]
    event.organizer = event_data.get("organizer", "michael@justbuildit.com")
    event.transparent = event_data.get("transparent", False)
    event.status = event_data.get("status", "confirmed")
    event.uid = f"parkcentury-{random.randint(10000, 99999)}"
    event.created = timezone.localize(datetime.strptime(event_data["created"], "%Y-%m-%d %H:%M"))
    event.last_modified = timezone.localize(datetime.strptime(event_data["last_modified"], "%Y-%m-%d %H:%M"))
    




    cal.events.add(event)

# Save to an iCal file
ical_path = "school_events_2024_2025.ics"
with open(ical_path, "w") as f:
    f.writelines(cal)

ical_path