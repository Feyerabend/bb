def activity_selection(start, finish):
    """
    Returns the maximum set of non-overlapping activities.
    
    Parameters:
    start (list): List of start times of activities
    finish (list): List of finish times of activities
    
    Returns:
    list: Indices of selected activities
    """
    # Create a list of activities as (start_time, finish_time, index)
    activities = [(start[i], finish[i], i) for i in range(len(start))]
    
    # Sort activities by finish time
    activities.sort(key=lambda x: x[1])
    
    # Select the first activity
    selected = [activities[0][2]]
    last_finish_time = activities[0][1]
    
    # Consider rest of the activities
    for i in range(1, len(activities)):
        # If this activity starts after the last finish time, select it
        if activities[i][0] >= last_finish_time:
            selected.append(activities[i][2])
            last_finish_time = activities[i][1]
    
    return selected


if __name__ == "__main__":
    start_times = [1, 3, 0, 5, 8, 5]
    finish_times = [2, 4, 6, 7, 9, 9]
    
    selected_activities = activity_selection(start_times, finish_times)
    
    print("Selected activities:", selected_activities)
    print("Number of activities selected:", len(selected_activities))
    
    print("\nSelected activities details:")
    for idx in selected_activities:
        print(f"Activity {idx}: Start time = {start_times[idx]}, Finish time = {finish_times[idx]}")
