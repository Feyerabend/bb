#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int start;
    int finish;
    int index;
} Activity;

int compareActivities(const void* a, const void* b) {
    Activity* act1 = (Activity*)a;
    Activity* act2 = (Activity*)b;
    return act1->finish - act2->finish;
}

int* activitySelection(int start[], int finish[], int n, int* count) {
    // Create an array of activities
    Activity* activities = (Activity*)malloc(n * sizeof(Activity));
    for (int i = 0; i < n; i++) {
        activities[i].start = start[i];
        activities[i].finish = finish[i];
        activities[i].index = i;
    }
    
    // Sort activities by finish time
    qsort(activities, n, sizeof(Activity), compareActivities);
    
    // Allocate memory for result (max possible size is n)
    int* selected = (int*)malloc(n * sizeof(int));
    *count = 0;
    
    // Select first activity
    selected[(*count)++] = activities[0].index;
    int last_finish = activities[0].finish;
    
    // Consider remaining activities
    for (int i = 1; i < n; i++) {
        // If this activity starts after the last finish time, select it
        if (activities[i].start >= last_finish) {
            selected[(*count)++] = activities[i].index;
            last_finish = activities[i].finish;
        }
    }

    free(activities);    
    return selected;
}

int main() {
    int start[] = {1, 3, 0, 5, 8, 5};
    int finish[] = {2, 4, 6, 7, 9, 9};
    int n = sizeof(start) / sizeof(start[0]);
    int count = 0;
    
    int* selected = activitySelection(start, finish, n, &count);
    
    printf("Selected activities: ");
    for (int i = 0; i < count; i++) {
        printf("%d ", selected[i]);
    }
    printf("\nNumber of activities selected: %d\n", count);
    
    printf("\nSelected activities details:\n");
    for (int i = 0; i < count; i++) {
        printf("Activity %d: Start time = %d, Finish time = %d\n", 
               selected[i], start[selected[i]], finish[selected[i]]);
    }
    
    free(selected);    
    return 0;
}
