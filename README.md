# DAA Maze Runner - Enhanced Graph Visualization

# Duel of Labyrinth

[![Play Online](https://img.shields.io/badge/Play-Online-green?style=for-the-badge&logo=google-chrome)](https://vidyadhar-pothula.github.io/DAA-Maze-Runner/)

A maze exploration game where you compete against a Greedy Best-First Search AI.

**[View Algorithm Implementations (Code Reference)](ALGORITHMS.md)**

## 🎯 Features

### Core Algorithm Features
- **Pure Greedy Best-First Search**: Demonstrates greedy algorithm behavior with heuristic-based decisions
- **Graph-Based Architecture**: Explicit graph representation with adjacency lists and edge weights
- **Real-time Performance Metrics**: Track nodes explored, visited, backtracking, and efficiency
- **Educational Annotations**: See AI decision-making process in real-timenope not ata

### Visualization Features
- **Graph Overlay Mode**: Toggle to see actual graph edges and connectivity
- **Heuristic Display**: View calculated heuristic values for each node
- **AI Annotation Mode**: Watch AI evaluate candidates and make decisions
- **Fog of War**: Player exploration mechanic for engaging gameplay
- **Path Trails**: Visual feedback for player and AI paths

### Performance Analysis
- **Efficiency Ratio**: Compare greedy path vs optimal path length
- **Exploration Percentage**: See how much of the graph was explored
- **Backtrack Counter**: Track algorithm failures and recoveries
- **Real-time Metrics Panel**: Live statistics during gameplay

## 📊 Graph Theory Implementation

### Graph Structure
```
- Nodes: Grid cells (excluding walls)
- Edges: 8-directional connectivity (cardinal + diagonal)
- Edge Weights: 
  * Normal: 1
  * Trap: 3
  * Powerup: -2
  * Wall: ∞ (unreachable)
```

### Greedy Algorithm Details
```python
# Greedy Best-First Search
1. Start at initial node
2. Evaluate all unvisited neighbors
3. Choose neighbor with MINIMUM heuristic value
4. Move to chosen node
5. If dead end → backtrack
6. Repeat until goal reached
```

**Key Characteristics**:
- Time Complexity: O(b^d) worst case, where b = branching factor, d = depth
- Space Complexity: O(bd) for frontier storage
- Optimality: NOT guaranteed (can find suboptimal paths)
- Completeness: YES (with backtracking in finite graphs)

### Heuristic Functions
```python
# Euclidean (default)
h(n) = √[(n.x - goal.x)² + (n.y - goal.y)²]

# Manhattan (optional)
h(n) = |n.x - goal.x| + |n.y - goal.y|

# Chebyshev (optional)
h(n) = max(|n.x - goal.x|, |n.y - goal.y|)
```

## 🚀 Installation

### Requirements
```bash
Python 3.8+
pygame >= 2.0.0
```

### Setup
```bash
# Install dependencies
pip install pygame

# Run the game
python main.py

# Run tests
python test_game.py
```

## 🎮 Controls

### Menu
- **1, 2, 3**: Select difficulty (Easy/Medium/Hard)
- **ENTER**: Start game

### Gameplay
- **WASD / Arrow Keys**: Move player (cardinal directions)
- **Q, E, Z, C**: Move player (diagonal directions)
- **G**: Toggle graph edge visualization
- **H**: Toggle heuristic value display
- **A**: Toggle AI decision annotations
- **SPACE**: Pause / Enable step-by-step mode

### Game Elements
- **S (Yellow)**: Start position
- **G (Purple)**: Goal position
- **Blue Circle**: Player
- **Orange Square**: Greedy AI
- **Red Circles**: Traps (cost = 3)
- **Green Circles**: Powerups (cost = -2)
- **Grey**: Walls (impassable)
- **White**: Open paths

## 📈 Performance Metrics Explained

### Nodes Explored
Number of nodes AI **considered** (added to evaluation frontier)
- Higher = more thorough search
- Greedy typically explores fewer nodes than A* or Dijkstra

### Nodes Visited
Number of nodes AI **actually moved to**
- This is the path length
- Compare to optimal path to measure efficiency

### Backtrack Count
How many times AI hit dead end and had to reverse
- Higher = more mistakes in greedy choices
- Demonstrates greedy's lack of global planning

### Exploration Percentage
`(nodes_explored / total_walkable_nodes) × 100`
- Greedy typically explores 20-40% of graph
- A* might explore 50-70%
- Dijkstra explores ~100%

### Efficiency Ratio
`optimal_path_length / ai_path_length × 100`
- 100% = AI found optimal path
- 50% = AI took 2× longer than optimal
- Demonstrates greedy's solution quality

## 🎓 Educational Use Cases

### 1. Algorithm Comparison
Compare greedy with other algorithms (future enhancement):
```
Scenario: Large maze with traps

Greedy:     Fast, 60% efficiency, 25% exploration
A*:         Slower, 95% efficiency, 50% exploration  
Dijkstra:   Slowest, 100% efficiency, 100% exploration
```

### 2. Heuristic Analysis
Test different heuristics to see impact:
- Euclidean: Best for open spaces
- Manhattan: Better for grid-restricted movement
- Chebyshev: Optimized for diagonal movement

### 3. Graph Properties Study
Learn graph theory concepts:
- **Connectivity**: How nodes connect
- **Cycles**: Multiple paths between nodes
- **Weighted Edges**: Different movement costs
- **Dead Ends**: Local minima in search space

### 4. Algorithm Limitations
Observe greedy failures:
- Gets trapped in local minima
- Ignores long-term costs (traps)
- Misses optimal powerup routes
- Requires backtracking for correction

## 🔬 Real-World Applications

### Where Greedy Works Well
1. **GPS Navigation** (with good heuristics): Quick route suggestions
2. **Game AI** (real-time constraints): Fast NPC pathfinding
3. **Network Routing** (low latency): Quick packet forwarding
4. **Resource Allocation** (immediate needs): Greedy task scheduling

### Where Greedy Fails
1. **Optimal Planning** (need best solution): Use A* or Dijkstra
2. **Cost-Sensitive** (must minimize cost): Weighted graph algorithms
3. **Long-term Strategy** (future consequences): Dynamic programming
4. **Adversarial** (opponent planning): Minimax, MCTS

## 📝 Code Architecture

### File Structure
```
game_classes.py
├── Node                  # Graph node with tracking
├── Maze                  # Graph structure + generation
├── PerformanceMetrics    # Algorithm analysis
├── Player                # Human player
└── GreedyAI              # Greedy best-first search

main.py
└── GameController        # Game loop + visualization

test_game.py
└── Comprehensive test suite
```

### Key Classes

**Node** - Graph vertex
```python
- position (r, c)
- type (path, wall, trap, powerup)
- cost (edge weight)
- tracking flags (visited, explored, times_evaluated)
```

**Maze** - Graph structure
```python
- adjacency_list: {node → [(neighbor, weight)]}
- heuristic functions (euclidean, manhattan, chebyshev)
- optimal path calculation (BFS)
- random generation (DFS maze carving)
```

**GreedyAI** - Algorithm implementation
```python
- choose_move(): Greedy decision logic
- metrics: Performance tracking
- decision_history: Audit trail
- backtracking: Dead-end recovery
```

## 🧪 Testing

Run comprehensive test suite:
```bash
python test_game.py

# Expected output:
# - Graph structure tests
# - Greedy algorithm behavior tests
# - Performance metrics tests
# - Edge case tests
```

### Test Coverage
- ✅ Graph construction and connectivity
- ✅ Greedy decision-making logic
- ✅ Backtracking on dead ends
- ✅ Heuristic calculations
- ✅ Performance metric tracking
- ✅ Maze generation reproducibility
- ✅ Player movement validation
- ✅ Edge cases (tiny mazes, walls)

## 📚 Learning Outcomes

After using this tool, students will understand:

1. **Graph Representation**
   - Adjacency lists vs matrices
   - Weighted vs unweighted graphs
   - Connected vs disconnected graphs

2. **Greedy Algorithm**
   - How greedy choices work
   - Why greedy isn't always optimal
   - When greedy performs well/poorly

3. **Heuristic Functions**
   - Admissible vs non-admissible
   - Impact on algorithm behavior
   - Trade-offs between heuristics

4. **Algorithm Analysis**
   - Time/space complexity
   - Optimality guarantees
   - Practical performance metrics

5. **Search Strategies**
   - Greedy vs A* vs Dijkstra
   - Informed vs uninformed search
   - Backtracking and recovery

## 🎯 Future Enhancements

### Priority Features
1. **A* Algorithm**: Compare optimal vs greedy
2. **Dijkstra Algorithm**: Cost-optimal pathfinding
3. **Replay System**: Save and review runs
4. **Custom Scenarios**: Load predefined trap mazes
5. **Leaderboard**: Track best efficiency scores

### Advanced Features
1. **Multiple Heuristics**: Switch between distance functions
2. **Algorithm Race**: Run 4 AIs simultaneously
3. **Heat Maps**: Visualize exploration density
4. **Export Statistics**: CSV data for analysis
5. **Educational Mode**: Step-by-step explanations

## 📖 References

### Algorithm Theory
- Introduction to Algorithms (CLRS) - Chapter 24
- Artificial Intelligence: A Modern Approach (Russell & Norvig) - Chapter 3
- Algorithm Design Manual (Skiena) - Chapter 6

### Real-world Tools
- Pathfinding.js - JavaScript pathfinding library
- VisuAlgo.net - Algorithm visualization
- Algorithm Visualizer - Interactive algorithm demos

### Graph Theory
- Graph Theory (Diestel) - Chapter 1-2
- Networks (Newman) - Chapter 6

## 🤝 Contributing

This is an educational project. Potential improvements:

1. Add more pathfinding algorithms (A*, Dijkstra, DFS, BFS)
2. Implement different maze generation algorithms (Kruskal's, Prim's)
3. Add more sophisticated visualization (3D, animations)
4. Create curriculum-aligned lesson plans
5. Build web-based version (PyScript/WASM)

## 📄 License

Educational use - Free to use and modify for learning purposes.

## 🎓 Academic Context

**Course**: Design and Analysis of Algorithms (DAA)
**Topics**: Graph algorithms, greedy strategies, heuristic search
**Level**: Undergraduate Computer Science (Year 2-3)

---

**Built for educational demonstration of graph algorithms and greedy search strategies.**

*Maze generation uses DFS recursive backtracking. Greedy algorithm implements best-first search with Euclidean heuristic and backtracking support.*