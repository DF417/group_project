## Goals
find an optimized schedule

### Tasks have
- dependencies
- priority
- limited resources (workers, machines, etc.)
- strict deadlines
- dynamic modification

### Optional
- variable durations (not implemented)

## Strategy

#### Path Calculation
Directed Acyclic Graph
Only topological paths are explored
Backtracking (DFS)
dynamic programming
- bottom up approach
- memoization
- 0/1 knapsack problem

To find all permutations ignoring topological order would be 
$O(n!)$

Our worst case:
$O(T × n × W)$
- $T$ = maximum time steps until completion
- $n$ = number of tasks
- $W$ = number of workers

#### Unused Methods
Libraries
top-down
Mixed Integer Linear Programming
Constraint Programming
Greedy Algorithms
Heuristic Search

