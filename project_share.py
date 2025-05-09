import heapq
from typing import List, Tuple, Dict, Set

# --- Task Definition ---
class Task:
    def __init__(self, id: str, duration: int, dependencies: List[str], workers_required: int, 
                 priority: int = 1, deadline: int = None):
        self.id = id
        self.duration = duration
        self.dependencies = dependencies
        self.workers_required = workers_required
        self.priority = priority
        self.deadline = deadline

# --- Scheduler Class ---
class Scheduler:
    def __init__(self, tasks: Dict[str, Task], total_workers: int):
        self.tasks = tasks
        self.total_workers = total_workers
        self.completed: Set[str] = set()
        self.in_progress: Dict[str, Tuple[int, Task]] = {}
        self.events: List[Tuple[int, str]] = []
        self.schedule: List[Tuple[int, List[str]]] = []
        self.time = 0

    def add_task(self, task: Task):
        self.tasks[task.id] = task

    def remove_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]

    def update_task_priority(self, task_id: str, new_priority: int):
        if task_id in self.tasks:
            self.tasks[task_id].priority = new_priority

    def get_ready_tasks(self) -> List[Task]:
        ready = []
        for task_id, task in self.tasks.items():
            if task_id in self.completed or task_id in self.in_progress:
                continue
            if all(dep in self.completed for dep in task.dependencies):
                ready.append(task)
        return ready

    def knapsack(self, tasks: List[Task], W: int) -> List[Task]:
        n = len(tasks)
        dp = [0.0] * (W + 1)
        track = [set() for _ in range(W + 1)]

        for i, task in enumerate(tasks):
            # Time-aware score: prioritize shorter, high-priority tasks
            score = task.priority / task.duration
            for w in range(W, task.workers_required - 1, -1):
                if dp[w - task.workers_required] + score > dp[w]:
                    dp[w] = dp[w - task.workers_required] + score
                    track[w] = track[w - task.workers_required].copy()
                    track[w].add(i)

        best_w = max(range(W + 1), key=lambda i: dp[i])
        return [tasks[i] for i in track[best_w]]

    def step(self):
        while self.events and self.events[0][0] <= self.time:
            end_time, task_id = heapq.heappop(self.events)
            self.completed.add(task_id)
            del self.in_progress[task_id]

        workers_in_use = sum(task.workers_required for _, task in self.in_progress.values())
        available_workers = self.total_workers - workers_in_use

        ready_tasks = self.get_ready_tasks()
        selected_tasks = self.knapsack(ready_tasks, available_workers)

        for task in selected_tasks:
            finish_time = self.time + task.duration
            self.in_progress[task.id] = (finish_time, task)
            heapq.heappush(self.events, (finish_time, task.id))

        if selected_tasks:
            self.schedule.append((self.time, [task.id for task in selected_tasks]))

        if not selected_tasks and self.events:
            self.time = self.events[0][0]
        else:
            self.time += 1

    def run(self):
        while len(self.completed) < len(self.tasks):
            self.step()
        return self.schedule

    def check_deadlines(self) -> Dict[str, str]:
        task_end_times = {}
        for time, task_ids in self.schedule:
            for task_id in task_ids:
                end = time + self.tasks[task_id].duration
                task_end_times[task_id] = end

        deadlines_status = {}
        for task_id, task in self.tasks.items():
            if task.deadline is not None:
                deadlines_status[task_id] = "Met" if task_end_times.get(task_id, float('inf')) <= task.deadline else "Missed"
        return deadlines_status

# --- Example Usage ---
tasks_input = {
    'A': Task('A', 2, [], 1),
    'B': Task('B', 3, ['A'], 2),
    'C': Task('C', 4, ['A'], 1),
    'D': Task('D', 2, ['B', 'C'], 3),
    'E': Task('E', 5, ['B'], 2),
    'F': Task('F', 3, ['D', 'E'], 1, deadline=12)
}

scheduler = Scheduler(tasks_input, total_workers=3)
schedule = scheduler.run()

print("\nSchedule (Time Step → Tasks Started):")
for time, task_ids in schedule:
    print(f"  Time {time}: Start tasks {task_ids}")

print("\nDeadline Status:")
deadline_results = scheduler.check_deadlines()
for task_id, status in deadline_results.items():
    print(f"  Task {task_id}: Deadline {status}")
