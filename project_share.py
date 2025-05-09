import heapq
from typing import List, Dict, Tuple, Optional

# Represents an individual task with metadata like duration, dependencies, etc.
class Task:
    def __init__(self, id: str, duration: int, dependencies: List[str], workers_required: int,
                 priority: int = 1, deadline: Optional[int] = None):
        self.id = id
        self.duration = duration
        self.dependencies = dependencies
        self.workers_required = workers_required
        self.priority = priority
        self.deadline = deadline

    def __repr__(self):
        # Human-readable representation, helpful for debugging
        return (f"Task(id={self.id}, duration={self.duration}, deps={self.dependencies}, "
                f"workers={self.workers_required}, priority={self.priority}, deadline={self.deadline})")

# Scheduler that assigns tasks incrementally based on resource constraints
class IncrementalScheduler:
    def __init__(self, tasks: Dict[str, Task], total_workers: int):
        self.tasks = tasks                                  # All tasks by ID
        self.total_workers = total_workers                  # Total workers available
        self.time = 0                                       # Current time unit
        self.completed = set()                              # Set of completed task IDs
        self.in_progress: Dict[str, Tuple[int, Task]] = {}  # Tasks currently in progress
        self.events: List[Tuple[int, str]] = []             # Min-heap of (end_time, task_id)
        self.schedule: List[Tuple[int, List[str], List[str]]] = []  # Log of each time step
        self.task_end_times: Dict[str, int] = {}            # Records actual end times

    def get_ready_tasks(self) -> List[Task]:
        # Returns tasks that are ready to start (not started, not completed, dependencies met)
        return [
            task for task_id, task in self.tasks.items()
            if task_id not in self.completed
            and task_id not in self.in_progress
            and all(dep in self.completed for dep in task.dependencies)
        ]

    def knapsack(self, tasks: List[Task], available_workers: int) -> List[Task]:
        # Solves a 0/1 knapsack problem to select tasks that maximize priority within worker limits
        dp = [0] * (available_workers + 1)                  # Max priority achievable with w workers
        track = [set() for _ in range(available_workers + 1)]  # Track selected task indices

        for i, task in enumerate(tasks):
            for w in range(available_workers, task.workers_required - 1, -1):
                if dp[w - task.workers_required] + task.priority > dp[w]:
                    dp[w] = dp[w - task.workers_required] + task.priority
                    track[w] = track[w - task.workers_required].copy()
                    track[w].add(i)

        # Reconstruct the best task list
        best_w = max(range(available_workers + 1), key=lambda i: dp[i])
        return [tasks[i] for i in track[best_w]]

    def step(self) -> bool:
        # Advances the scheduler by one time unit
        if len(self.completed) == len(self.tasks):
            return False

        just_completed = []

        # Handle tasks completing at current time
        while self.events and self.events[0][0] <= self.time:
            end_time, task_id = heapq.heappop(self.events)
            self.completed.add(task_id)
            just_completed.append(task_id)
            del self.in_progress[task_id]
            self.task_end_times[task_id] = end_time

        # Determine available workers
        workers_used = sum(task.workers_required for _, task in self.in_progress.values())
        available_workers = self.total_workers - workers_used

        # Find and select tasks to start
        ready = self.get_ready_tasks()
        selected = self.knapsack(ready, available_workers)

        just_started = []

        # Start selected tasks
        for task in selected:
            finish_time = self.time + task.duration
            self.in_progress[task.id] = (finish_time, task)
            heapq.heappush(self.events, (finish_time, task.id))
            just_started.append(task.id)

        # Log schedule info
        self.schedule.append((self.time, just_started, just_completed))

        # Output status
        print(f"\nTime: {self.time}")
        print(f"Completed this step: {just_completed}")
        print(f"Started this step: {just_started}")
        print("In Progress:")
        for tid, (ft, t) in self.in_progress.items():
            print(f"  - {tid} (ends at {ft})")

        # Check deadlines
        for tid in just_completed:
            task = self.tasks[tid]
            if task.deadline is not None:
                status = "Met" if self.task_end_times[tid] <= task.deadline else "Missed"
                print(f"Deadline check for {tid}: {status} (Deadline: {task.deadline}, Ended: {self.task_end_times[tid]})")

        self.time += 1
        return True

    def run_interactive(self):
        # Interactive loop: executes steps and accepts dynamic modifications
        while True:
            proceed = self.step()
            if not proceed:
                break
            command = input("\nPress Enter to continue or type 'add', 'mod', 'del', 'exit': ").strip().lower()
            if command == "add":
                self.add_task_prompt()
            elif command == "mod":
                self.modify_task_prompt()
            elif command == "del":
                self.delete_task_prompt()
            elif command == "exit":
                print("Exiting scheduler.")
                break

        # Final output
        print("\nFinal Task Completion Times:")
        for task_id, end_time in self.task_end_times.items():
            task = self.tasks[task_id]
            deadline_info = ""
            if task.deadline is not None:
                status = "Met" if end_time <= task.deadline else "Missed"
                deadline_info = f" | Deadline: {task.deadline} ({status})"
            print(f"  - Task {task_id}: completed at {end_time}{deadline_info}")

    def add_task_prompt(self):
        # Prompt user to add a new task interactively
        print("Add a new task")
        id = input("ID: ").strip()
        duration = int(input("Duration: "))
        deps = input("Dependencies (comma separated): ").strip().split(",") if input("Dependencies? (y/n): ").strip().lower() == 'y' else []
        deps = [d.strip() for d in deps if d.strip()]
        workers = int(input("Workers required: "))
        priority = int(input("Priority (default 1): ") or "1")
        deadline_input = input("Deadline (optional): ").strip()
        deadline = int(deadline_input) if deadline_input else None
        self.tasks[id] = Task(id, duration, deps, workers, priority, deadline)
        print(f"Task {id} added.")

    def modify_task_prompt(self):
        # Prompt user to modify an existing task
        id = input("Enter task ID to modify: ").strip()
        if id not in self.tasks:
            print("Task not found.")
            return
        task = self.tasks[id]
        print(f"Current: {task}")
        duration = input(f"Duration ({task.duration}): ").strip()
        workers = input(f"Workers required ({task.workers_required}): ").strip()
        priority = input(f"Priority ({task.priority}): ").strip()
        deadline = input(f"Deadline ({task.deadline}): ").strip()
        deps = input(f"Dependencies (comma separated) [{', '.join(task.dependencies)}]: ").strip()

        # Apply modifications
        task.duration = int(duration) if duration else task.duration
        task.workers_required = int(workers) if workers else task.workers_required
        task.priority = int(priority) if priority else task.priority
        task.deadline = int(deadline) if deadline else task.deadline
        if deps:
            task.dependencies = [d.strip() for d in deps.split(",") if d.strip()]
        print(f"Task {id} updated.")

    def delete_task_prompt(self):
        # Prompt user to delete a task
        id = input("Enter task ID to delete: ").strip()
        if id in self.tasks:
            del self.tasks[id]
            print(f"Task {id} deleted.")
        else:
            print("Task not found.")

# --- Sample Usage ---
# Define initial tasks
tasks_input = {
    'A': Task('A', 2, [], 1),
    'B': Task('B', 3, ['A'], 2),
    'C': Task('C', 4, ['A'], 1),
    'D': Task('D', 2, ['B', 'C'], 3),
    'E': Task('E', 5, ['B'], 2),
    'F': Task('F', 3, ['D', 'E'], 1, deadline=12),
}

# Create scheduler instance and run interactively
scheduler = IncrementalScheduler(tasks_input, total_workers=4)
scheduler.run_interactive()
