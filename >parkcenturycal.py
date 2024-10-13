from datetime import datetime, timedelta
import pytz
import ics
from ics import Calendar, Event

# Create a calendar
cal = Calendar()
timezone = pytz.timezone("America/Los_Angeles")

# Define events
events = [
    {"summary": "PC--Back-to-School Social", "start": "2024-09-03 10:00", "end": "2024-09-03 14:00"},
    {"summary": "PC--First Day of School (Minimum Day)", "start": "2024-09-04 08:45", "end": "2024-09-04 15:15"},
    {"summary": "PC--Back-to-School BBQ", "start": "2024-09-21 17:00", "end": "2024-09-21 19:00"},
    {"summary": "PC--Minimum Day / MS Back-to-School Night", "start": "2024-09-25 12:00", "end": "2024-09-25 20:00"},
    {"summary": "PC--Minimum Day / LS Back-to-School Night", "start": "2024-10-09 12:00", "end": "2024-10-09 20:00"},
    {"summary": "PC--Faculty Professional Development", "start": "2024-11-08 00:00", "end": "2024-11-08 23:59"},
    {"summary": "PC--Faculty Professional Development", "start": "2024-11-11 00:00", "end": "2024-11-11 23:59"},
    {"summary": "PC--Parent Association Gratitude Celebration", "start": "2024-11-22 12:00", "end": "2024-11-22 15:00"},
    {"summary": "PC--Parent Conferences", "start": "2024-12-12 00:00", "end": "2024-12-13 23:59"},
    {"summary": "PC--Fine Arts Showcase / Minimum Day", "start": "2024-12-18 12:00", "end": "2024-12-18 15:00"},
    {"summary": "PC--Faculty Professional Development", "start": "2025-01-06 00:00", "end": "2025-01-06 23:59"},
    {"summary": "PC--Classes Resume", "start": "2025-01-07 08:00", "end": "2025-01-07 17:00"},
    {"summary": "PC--Grandparents and Special Friends Day / Minimum Day", "start": "2025-03-21 09:30", "end": "2025-03-21 15:00"},
    {"summary": "PC--Faculty Professional Development", "start": "2025-04-07 00:00", "end": "2025-04-07 23:59"},
    {"summary": "PC--Faculty Professional Development", "start": "2025-05-05 00:00", "end": "2025-05-05 23:59"},
    {"summary": "PC--Teacher Appreciation Lunch / Minimum Day", "start": "2025-05-09 12:00", "end": "2025-05-09 15:00"},
    {"summary": "PC--Minimum Day", "start": "2025-05-23 12:00", "end": "2025-05-23 15:00"},
    {"summary": "PC--Parent Conferences", "start": "2025-05-29 00:00", "end": "2025-05-30 23:59"},
    {"summary": "PC--Last Day of School / Field Day", "start": "2025-06-04 08:00", "end": "2025-06-04 15:00"},
    {"summary": "PC--Classroom Parties", "start": "2025-06-05 08:00", "end": "2025-06-05 17:00"},
    {"summary": "PC--8th Grade Graduation", "start": "2025-06-06 08:00", "end": "2025-06-06 17:00"},
    {"summary": "PC--Early Dismissal", "start": "2024-09-20 14:00", "end": "2024-09-20 14:30"},
    {"summary": "PC--Early Dismissal", "start": "2024-10-18 14:00", "end": "2024-10-18 14:30"},
    {"summary": "PC--Early Dismissal", "start": "2025-01-31 14:00", "end": "2025-01-31 14:30"},
    {"summary": "PC--Early Dismissal", "start": "2025-02-28 14:00", "end": "2025-02-28 14:30"},
    {"summary": "PC--Early Dismissal", "start": "2025-04-25 14:00", "end": "2025-04-25 14:30"},
]

# Add events to calendar
for event_data in events:
    event = Event()
    event.name = event_data["summary"]
    event.begin = timezone.localize(datetime.strptime(event_data["start"], "%Y-%m-%d %H:%M"))
    event.end = timezone.localize(datetime.strptime(event_data["end"], "%Y-%m-%d %H:%M"))
    cal.events.add(event)

# Save to an iCal file
ical_path = "/Users/michasmi/school_events_2024_2025.ics"
with open(ical_path, "w") as f:
    f.writelines(cal)

# ical_path