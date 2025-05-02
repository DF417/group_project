import heapq
from typing import List, Tuple, Dict

# --- Task Definition ---
class Task:
    def __init__(self, id: str, duration: int, dependencies: List[str], workers_required: int, 
                 priority: int = 1, deadline: int = None):
        """Initialize a task with ID, duration, dependencies, workers required, priority, and optional deadline."""
        self.id = id
        self.duration = duration
        self.dependencies = dependencies
        self.workers_required = workers_required
        self.priority = priority
        self.deadline = deadline  # Optional (not enforced yet)

# --- Get Tasks Ready to Start ---
def get_ready_tasks(tasks: Dict[str, Task], completed: set, in_progress: Dict[str, Tuple[int, Task]]) -> List[Task]:
    """
    Return a list of tasks that are ready to start.
    A task is ready if all its dependencies have been completed and it is not already in progress.
    """
    ready = []
    for task_id, task in tasks.items():
        # Skip tasks that are already completed or in progress
        if task_id in completed or task_id in in_progress:
            continue
        # Task is ready if all its dependencies are completed
        if all(dep in completed for dep in task.dependencies):
            ready.append(task)
    return ready

# --- 0/1 Knapsack Subroutine to Select Tasks Within Worker Limits ---
def knapsack(tasks: List[Task], W: int) -> List[Task]:
    """
    Use 0/1 knapsack to select a subset of tasks within the worker limit, maximizing priority.
    This helps to select tasks that can be scheduled within the available worker limit.
    """
    n = len(tasks)
    dp = [0] * (W + 1)  # DP table to store the maximum priority achievable for each worker count
    track = [set() for _ in range(W + 1)]  # Track selected tasks

    for i, task in enumerate(tasks):
        for w in range(W, task.workers_required - 1, -1):
            # If including this task results in a higher priority, select it
            if dp[w - task.workers_required] + task.priority > dp[w]:
                dp[w] = dp[w - task.workers_required] + task.priority
                track[w] = track[w - task.workers_required].copy()
                track[w].add(i)

    # Get the subset of tasks that gives the maximum priority
    best_w = max(range(W + 1), key=lambda i: dp[i])
    return [tasks[i] for i in track[best_w]]

# --- Main Scheduling Function ---
def schedule_tasks(tasks: Dict[str, Task], total_workers: int) -> List[Tuple[int, List[str]]]:
    """
    Schedule tasks with dependencies, worker limits, and task durations.
    Use a knapsack subroutine to select the best subset of tasks based on available workers and task priority.
    """
    time = 0  # Start time
    completed = set()  # Set of completed tasks
    in_progress: Dict[str, Tuple[int, Task]] = {}  # Dictionary of tasks currently in progress
    events = []  # Min-heap of (end_time, task_id), used to track task completion
    schedule = []  # List to store the scheduled tasks for each time step

    # Continue scheduling until all tasks are completed
    while len(completed) < len(tasks):
        # Complete tasks finishing at the current time
        while events and events[0][0] <= time:
            end_time, task_id = heapq.heappop(events)
            completed.add(task_id)  # Mark task as completed
            del in_progress[task_id]  # Remove from in-progress

        # Calculate available workers
        workers_in_use = sum(task.workers_required for _, task in in_progress.values())
        available_workers = total_workers - workers_in_use  # Remaining workers available

        # Find tasks that are ready to start (i.e., dependencies are complete)
        ready_tasks = get_ready_tasks(tasks, completed, in_progress)

        # Select the subset of tasks to start using the knapsack approach
        selected_tasks = knapsack(ready_tasks, available_workers)

        # Start selected tasks
        for task in selected_tasks:
            finish_time = time + task.duration
            in_progress[task.id] = (finish_time, task)  # Track the task in progress
            heapq.heappush(events, (finish_time, task.id))  # Add task's finish time to event queue

        # Log the selected tasks for this time step
        if selected_tasks:
            schedule.append((time, [task.id for task in selected_tasks]))

        # Advance time (either progress time or jump to the next event)
        if not selected_tasks and events:
            time = events[0][0]  # Jump to the earliest event time
        else:
            time += 1  # Increment time by 1 if no events are scheduled

    return schedule

# --- Function to Check If Deadlines Are Met ---
def check_deadlines(tasks: Dict[str, Task], schedule: List[Tuple[int, List[str]]]) -> Dict[str, bool]:
    """
    Check if any tasks miss their deadlines. Returns a dictionary with task IDs as keys and
    True if the task was completed on time, False if it missed the deadline.
    """
    task_end_times = {task_id: 0 for task_id in tasks}
    
    # Track the end time of each task
    for time, task_ids in schedule:
        for task_id in task_ids:
            task_end_times[task_id] = time + tasks[task_id].duration

    # Check if any task missed its deadline
    deadlines_met = {}
    for task_id, task in tasks.items():
        if task.deadline is not None:  # Only check tasks with deadlines
            deadlines_met[task_id] = task_end_times[task_id] <= task.deadline
        else:
            deadlines_met[task_id] = True  # No deadline, task is considered on time

    return deadlines_met

# --- Sample Input (Matching Your Format) ---
tasks_input = {
    'A': Task('A', 2, [], 1),
    'B': Task('B', 3, ['A'], 2),
    'C': Task('C', 4, ['A'], 1),
    'D': Task('D', 2, ['B', 'C'], 3),
    'E': Task('E', 5, ['B'], 2),
    'F': Task('F', 3, ['D', 'E'], 1, deadline=12)  # Task F has a deadline
}

# --- Run Scheduler ---
total_workers = 3
schedule = schedule_tasks(tasks_input, total_workers)

# --- Print Schedule Output ---
print("\nSchedule (Time Step → Tasks Started):")
for time, task_ids in schedule:
    print(f"  Time {time}: Start tasks {task_ids}")

# --- Task Timings ---
print("\nTask Timings (Start → End):")
task_timings = {}
for time, task_ids in schedule:
    for task_id in task_ids:
        start = time
        end = start + tasks_input[task_id].duration
        task_timings[task_id] = (start, end)
        print(f"  Task {task_id}: {start} → {end}")

# --- Check Deadlines ---
deadlines_met = check_deadlines(tasks_input, schedule)

# Print out which tasks met their deadlines
print("\nDeadline Status:")
for task_id, met in deadlines_met.items():
    if not met:
        print(f"  Task {task_id}: Deadline Met")
    else:
        print(f"  Task {task_id}: Missed Deadline")
