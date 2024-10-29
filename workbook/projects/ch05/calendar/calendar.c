#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

#define MAX_EVENTS 100
#define MAX_LINE_LENGTH 256
#define MAX_SUMMARY_LENGTH 100
#define MAX_LOCATION_LENGTH 100

typedef struct {
    char summary[MAX_SUMMARY_LENGTH];
    char location[MAX_LOCATION_LENGTH];
    struct tm start;
    struct tm end;
} Event;

typedef struct {
    Event events[MAX_EVENTS];
    int event_count;
} Calendar;

// fwd decl
void parse_calendar(const char *file_path, Calendar *calendar);
void parse_event(char **event_lines, int line_count, Event *event);
void parse_datetime(const char *value, struct tm *datetime);
void trim_whitespace(char *str);
void print_events(const Calendar *calendar);

int main() {
    const char *file_path = "calendar.ics"; // replace with actual .ics file path
    Calendar calendar = { .event_count = 0 };

    parse_calendar(file_path, &calendar);
    print_events(&calendar);

    return 0;
}

void parse_calendar(const char *file_path, Calendar *calendar) {
    FILE *file = fopen(file_path, "r");
    if (!file) {
        perror("Error opening file");
        return;
    }

    char line[MAX_LINE_LENGTH];
    char *event_lines[MAX_LINE_LENGTH];
    int in_event = 0;
    int line_count = 0;

    while (fgets(line, sizeof(line), file)) {
        trim_whitespace(line);

        if (strcmp(line, "BEGIN:VEVENT") == 0) {
            in_event = 1;
            line_count = 0;

        } else if (strcmp(line, "END:VEVENT") == 0) {
            in_event = 0;
            Event event;
            parse_event(event_lines, line_count, &event);
            calendar->events[calendar->event_count++] = event;

        } else if (in_event) {
            event_lines[line_count] = strdup(line);
            line_count++;
        }
    }

    fclose(file);
}

void parse_event(char **event_lines, int line_count, Event *event) {
    for (int i = 0; i < line_count; i++) {
        char *line = event_lines[i];
        char key[MAX_LINE_LENGTH];
        char value[MAX_LINE_LENGTH];

        // line into key and value
        if (sscanf(line, "%[^:]:%[^\n]", key, value) == 2) {
            trim_whitespace(key);
            trim_whitespace(value);

            if (strncmp(key, "DTSTART", 7) == 0) {
                parse_datetime(value, &event->start);
            } else if (strncmp(key, "DTEND", 5) == 0) {
                parse_datetime(value, &event->end);
            } else if (strcmp(key, "SUMMARY") == 0) {
                strncpy(event->summary, value, MAX_SUMMARY_LENGTH);
            } else if (strcmp(key, "LOCATION") == 0) {
                strncpy(event->location, value, MAX_LOCATION_LENGTH);
            }
        }
        free(line); // free duplicated line
    }
}

void parse_datetime(const char *value, struct tm *datetime) {
    char buffer[20];
    const char *time_str;

    // remove timezone information if present
    if (strstr(value, ";") != NULL) {
        time_str = strtok(strdup(value), ";");
    } else {
        time_str = value;
    }

    // check if it contains time (format: YYYYMMDDTHHMMSS)
    if (strchr(time_str, 'T')) {
        sscanf(time_str, "%4d%2d%2dT%2d%2d%2d",
               &datetime->tm_year, &datetime->tm_mon, &datetime->tm_mday,
               &datetime->tm_hour, &datetime->tm_min, &datetime->tm_sec);
        datetime->tm_year -= 1900; // tm_year is years since 1900
        datetime->tm_mon -= 1;      // tm_mon is 0-11

    // date-only format (format: YYYYMMDD)
    } else {
        sscanf(time_str, "%4d%2d%2d",
               &datetime->tm_year, &datetime->tm_mon, &datetime->tm_mday);
        datetime->tm_hour = datetime->tm_min = datetime->tm_sec = 0;
        datetime->tm_year -= 1900;
        datetime->tm_mon -= 1;
    }
}

void trim_whitespace(char *str) {
    char *end;

    // trim leading space
    while (isspace((unsigned char)*str)) str++;

    // trim trailing space
    end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;

    // null terminate
    *(end + 1) = '\0';
}

void print_events(const Calendar *calendar) {
    for (int i = 0; i < calendar->event_count; i++) {
        const Event *event = &calendar->events[i];
        printf("Event: %s\n", event->summary);
        printf("Start: %04d-%02d-%02d %02d:%02d:%02d\n",
               event->start.tm_year + 1900, event->start.tm_mon + 1, event->start.tm_mday,
               event->start.tm_hour, event->start.tm_min, event->start.tm_sec);
        printf("End: %04d-%02d-%02d %02d:%02d:%02d\n",
               event->end.tm_year + 1900, event->end.tm_mon + 1, event->end.tm_mday,
               event->end.tm_hour, event->end.tm_min, event->end.tm_sec);
        printf("Location: %s\n\n", event->location);
    }
}