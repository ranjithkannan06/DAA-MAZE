# Algorithms Used in Duel of Labyrinth

This document provides the actual Python code implementations used in the game for reference.

## 1. Depth-First Search (DFS)
**Usage:** Maze Generation
**File:** `game_classes.py`

**Where & How:**
Used in the `Maze.__init__` method during the game's loading screen. It starts with a grid full of walls and uses a randomized DFS (recursive backtracking stack) to carve out paths, ensuring a perfect maze (no loops, fully connected) before we add extra loops and traps.

```python
def generate_random(self, width, height):
    # ... (Initialization)
    
    # DFS maze generation (creates graph paths)
    stack = [(0, 0)]
    visited = set([(0, 0)])
    
    while stack:
        current_r, current_c = stack[-1]
        
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        random.shuffle(directions)
        
        found_next = False
        for dr, dc in directions:
            nr, nc = current_r + dr, current_c + dc
            if 0 <= nr < height and 0 <= nc < width and (nr, nc) not in visited:
                # Carve path (create graph edge)
                wall_r, wall_c = current_r + dr // 2, current_c + dc // 2
                self.grid[wall_r][wall_c].type = '.'
                self.grid[nr][nc].type = '.'
                
                visited.add((nr, nc))
                stack.append((nr, nc))
                found_next = True
                break
        
        if not found_next:
            stack.pop()
```

## 2. Breadth-First Search (BFS)
**Usage:** Structural Analysis (Distance Map)
**File:** `game_classes.py`

**Where & How:**
Used in `Maze.bfs_analysis` immediately after maze generation. It runs a BFS starting from the **Goal Node** backwards to every other node. This creates a "perfect distance map" (cyan overlay) that shows the true shortest distance from any point to the goal, ignoring edge weights (traps).

```python
def bfs_analysis(self):
    """BFS for Structural Analysis (Distance Map)"""
    if not self.goal_node: return
    
    self.bfs_map = {}
    self.max_bfs_distance = 0
    
    queue = deque([(self.goal_node, 0)])
    self.bfs_map[self.goal_node] = 0
    
    while queue:
        node, dist = queue.popleft()
        self.max_bfs_distance = max(self.max_bfs_distance, dist)
        
        for neighbor in self.get_neighbors(node):
            if neighbor not in self.bfs_map:
                self.bfs_map[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))
```

## 3. A* (A-Star) Search
**Usage:** Optimal Path Calculation & Simulation
**File:** `game_classes.py`

**Where & How:**
1.  **Metrics:** Used in `Maze.a_star_optimal` at game start to calculate the "Optimal Cost". This value is used as the baseline (100% efficiency) to grade the player and Greedy AI.
2.  **Simulation:** Used in the "Simulation Mode" (Press 'S' at Game Over) to demonstrate the optimal path that considers both distance and edge costs (avoiding traps).

```python
def a_star_optimal(self):
    """A* for Optimal Reference Cost"""
    if not self.start_node or not self.goal_node: return 0
    
    frontier = PriorityQueue()
    frontier.put(self.start_node, 0)
    
    cost_so_far = {}
    cost_so_far[self.start_node] = 0
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == self.goal_node:
            break
        
        for neighbor in self.get_neighbors(current):
            # Calculate edge cost (1 for cardinal, 1.414 for diagonal)
            edge_cost = 1
            if abs(current.r - neighbor.r) + abs(current.c - neighbor.c) == 2:
                edge_cost = 1.414
            
            penalty = 0
            if neighbor.type == 'T': penalty = 3
            elif neighbor.type == 'P': penalty = -2
            
            new_cost = cost_so_far[current] + max(0.1, edge_cost + penalty)
            
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + self.heuristic(neighbor)
                frontier.put(neighbor, priority)
    
    return cost_so_far.get(self.goal_node, 0)
```

## 4. Heuristic Functions
**Usage:** Distance Calculation for Greedy/A*
**File:** `game_classes.py`

**Where & How:**
Used by **Greedy Best-First** and **A*** algorithms to estimate the distance to the goal.
*   **Euclidean**: Default for the main game AI.
*   **Manhattan/Chebyshev**: Available in Simulation Mode to show how different distance metrics change the path.

```python
def heuristic(self, node, heuristic_type='euclidean'):
    if heuristic_type == 'euclidean':
        return math.sqrt((node.r - self.goal_node.r)**2 + (node.c - self.goal_node.c)**2)
    elif heuristic_type == 'manhattan':
        return abs(node.r - self.goal_node.r) + abs(node.c - self.goal_node.c)
    elif heuristic_type == 'chebyshev':
        return max(abs(node.r - self.goal_node.r), abs(node.c - self.goal_node.c))
    return 0
```


## 5. Greedy Best-First Search (GBFS)
**Usage:** AI Agent Logic (Default)
**File:** `game_classes.py`

**Where & How:**
This is the **Main AI Opponent** you play against. It is designed to be fast and aggressive, prioritizing nodes that appear closest to the goal.

**Core Concept:** "Closer is Better."
Unlike Dijkstra (which minimizes total distance traveled) or A* (which balances distance traveled + distance to go), GBFS **only** considers the estimated distance to the goal. It uses a **Heuristic Function** to make this estimate.

**The Heuristics (The "Measuring Sticks"):**
The AI can use different mathematical formulas to estimate "closeness":

1.  **Euclidean Distance (Default)**
    *   **Formula:** $\sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$
    *   **Logic:** Measures the straight-line distance ("as the crow flies").
    *   **Behavior:** The AI tries to move directly towards the goal. It produces smooth, natural-looking paths in open areas.
    *   **Best For:** Maps where diagonal movement is allowed and costs roughly the same as cardinal movement.

2.  **Manhattan Distance (Taxicab Geometry)**
    *   **Formula:** $|x_1 - x_2| + |y_1 - y_2|$
    *   **Logic:** Measures distance as if traveling along a grid of city blocks (only Up/Down/Left/Right).
    *   **Behavior:** The AI prefers cardinal directions. It might overestimate distances in a game that allows diagonals, making it slightly more conservative.
    *   **Best For:** Grid-based games where diagonal movement is **not** allowed.

3.  **Chebyshev Distance (Chessboard Distance)**
    *   **Formula:** $\max(|x_1 - x_2|, |y_1 - y_2|)$
    *   **Logic:** Measures distance assuming you can move in any direction (including diagonals) for a cost of 1 (like a King in Chess).
    *   **Behavior:** It treats diagonals as "cheap" shortcuts. It can be very aggressive in cutting corners.
    *   **Best For:** Grids where diagonal movement costs the same as cardinal movement (Cost = 1).

**Pros:**
*   **Speed:** Very fast execution. It heads straight for the goal.
*   **Human-like:** Mimics visual intuition.

**Cons:**
*   **Not Optimal:** It might take a longer path or step on traps because it ignores the cost of the path traveled so far.
*   **Obstacles:** Can get stuck in "local optima" (e.g., running into a U-shaped wall).

```python
def compute_path_best_first(self):
    frontier = PriorityQueue()
    frontier.put(self.current_node, 0)
    
    came_from = {}
    came_from[self.current_node] = None
    
    while not frontier.empty():
        current = frontier.get()
        
        if current == self.goal_node:
            break
        
        for neighbor in self.maze.get_neighbors(current):
            if neighbor not in came_from:
                # Greedy: priority = heuristic(n)
                priority = self.heuristic(neighbor)
                frontier.put(neighbor, priority)
                came_from[neighbor] = current
```

## 6. Pure Greedy (Hill Climbing)
**Usage:** AI Simulation Mode (Educational Comparison)
**File:** `game_classes.py`

**Where & How:**
Only available in **Simulation Mode**. This is a "naive" version of greedy search that does not store a history or frontier. It simply moves to the best neighbor and forgets the rest. It is used to demonstrate how simple algorithms can get stuck in local minima (dead ends).

```python
def compute_path_hill_climbing(self):
    """Pure Greedy - No backtracking, can get stuck"""
    current = self.current_node
    while current != self.goal_node:
        neighbors = self.maze.get_neighbors(current)
        best_neighbor = None
        best_h = float('inf')
        
        # Find best unvisited neighbor
        for neighbor in neighbors:
            if neighbor not in visited:
                h = self.heuristic(neighbor)
                if h < best_h:
                    best_h = h
                    best_neighbor = neighbor
        
        if best_neighbor:
            current = best_neighbor
        else:
            # Dead end - Algorithm Fails
            break
```

## 7. Dijkstra's Algorithm
**Usage:** AI Simulation Mode (Optimal Path)
**File:** `game_classes.py`

**Where & How:**
Available in **Simulation Mode**. It explores the graph based *only* on accumulated cost (g-score), guaranteeing the shortest path. It is used to compare against A* (which is faster due to heuristics) and Greedy (which is faster but suboptimal).

```python
# Implemented within compute_path_best_first using 'dijkstra' mode
# Priority = Cost So Far (g_score)
new_cost = cost_so_far[current] + step_cost
if new_cost < cost_so_far[neighbor]:
    cost_so_far[neighbor] = new_cost
    priority = new_cost
    frontier.put(neighbor, priority)
```

## 8. Huffman Coding
**Usage:** Post-Game Data Compression Analysis
**File:** `game_classes.py`

**Where & How:**
Used in the **Game Over Screen**. It takes the AI's entire movement history (e.g., "MMMTM...") and calculates how much space could be saved by compressing it. This demonstrates a practical application of greedy algorithms in data compression.

```python
class Huffman:
    def build_tree(self, text):
        if not text: return None
        
        freqs = {}
        for char in text:
            freqs[char] = freqs.get(char, 0) + 1
            
        pq = []
        for char, freq in freqs.items():
            heapq.heappush(pq, HuffmanNode(char, freq))
            
        while len(pq) > 1:
            left = heapq.heappop(pq)
            right = heapq.heappop(pq)
            parent = HuffmanNode(None, left.freq + right.freq, left, right)
            heapq.heappush(pq, parent)
            
        root = heapq.heappop(pq)
        self.generate_codes(root, "")
        return root
```
