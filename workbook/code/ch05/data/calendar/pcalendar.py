import datetime

class SimpleICalendarParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.events = []
        self._parse_calendar()

    def _parse_line(self, line):
        # Skip empty lines
        if not line.strip():
            return None, None
        
        # Split by the first colon only
        parts = line.split(":", 1)
        if len(parts) < 2:
            return None, None  # Handle lines without a colon
        
        key, value = parts
        return key.strip(), value.strip()

    def _parse_event(self, event_lines):
        event = {}
        for line in event_lines:
            key, value = self._parse_line(line)
            if key is None:  # Skip if no valid key-value pair was returned
                continue
            
            if key.startswith("DTSTART"):
                event["start"] = self._parse_datetime(value)
            elif key.startswith("DTEND"):
                event["end"] = self._parse_datetime(value)
            elif key == "SUMMARY":
                event["summary"] = value
            elif key == "LOCATION":
                event["location"] = value
        return event

    def _parse_calendar(self):
        in_event = False
        event_lines = []

        with open(self.file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line == "BEGIN:VEVENT":
                    in_event = True
                    event_lines = []
                elif line == "END:VEVENT":
                    in_event = False
                    self.events.append(self._parse_event(event_lines))
                elif in_event:
                    event_lines.append(line)

    def _parse_datetime(self, value):
        # Remove timezone info if present, e.g., ;TZID=Europe/Berlin
        if ";" in value:
            value = value.split(";")[0]
        
        # Remove trailing 'Z' if it exists, which indicates UTC time
        value = value.rstrip('Z')

        # Check if it contains time
        if "T" in value:
            # Handle full datetime format
            return datetime.datetime.strptime(value, "%Y%m%dT%H%M%S")
        else:
            # Handle date-only format
            return datetime.datetime.strptime(value, "%Y%m%d")

    def get_events(self):
        return self.events

# Example usage
file_path = "calendar.ics"  # Replace with your actual .ics file path
parser = SimpleICalendarParser(file_path)
for event in parser.get_events():
    print("Event:", event.get("summary", "No Summary"))
    print("Start:", event.get("start", "No Start Date"))
    print("End:", event.get("end", "No End Date"))
    print("Location:", event.get("location", "No Location"))
    print()