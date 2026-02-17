import sys

class RegionLogic:
    """
    Centralized logic for Maze Region Partitioning (Islands & Bridges).
    Used by:
    1. DynamicMaze (to maintain real-time graph structure)
    2. RegionVisualizer (to animate the process)
    3. Main Game Loop (for static overlay drawing)
    """

    @staticmethod
    def compute_articulation_points(maze):
        """
        Run Tarjan's Algorithm to find Articulation Points (Bridges).
        Returns: set(Node)
        """
        visited = set()
        discovery_time = {}
        low_link = {}
        parent = {}
        articulation_points = set()
        time = 0
        
        # Helper to find start node
        start_node = maze.grid[0][0]
        if start_node.type == '#':
             for r in range(maze.height):
                 for c in range(maze.width):
                     if maze.grid[r][c].type != '#':
                         start_node = maze.grid[r][c]
                         break
                 if start_node.type != '#': break

        # Iterative DFS to avoid recursion limit
        stack = [(start_node, None, iter(maze.get_neighbors(start_node)))]
        visited.add(start_node)
        discovery_time[start_node] = low_link[start_node] = time
        time += 1
        children = 0
        
        while stack:
            u, p, neighbors = stack[-1]
            try:
                v = next(neighbors)
                if v == p: continue
                
                if v in visited:
                    low_link[u] = min(low_link[u], discovery_time[v])
                else:
                    parent[v] = u
                    visited.add(v)
                    discovery_time[v] = low_link[v] = time
                    time += 1
                    stack.append((v, u, iter(maze.get_neighbors(v))))
            except StopIteration:
                stack.pop()
                if p is not None:
                    low_link[p] = min(low_link[p], low_link[u])
                    if low_link[u] >= discovery_time[p]:
                        if p != start_node:
                            articulation_points.add(p)
                    # Root logic handled by children count
                elif stack:
                    # Returning to root
                    if stack[-1][0] == start_node:
                        children += 1

        if children > 1:
            articulation_points.add(start_node)
            
        return articulation_points

    @staticmethod
    def compute_regions(maze, articulation_points):
        """
        Partition maze into regions using Flood Fill, respecting APs as boundaries.
        Returns:
            regions_map: {node: region_id}
            region_graph: {region_id: set(connected_region_ids)}
            regions_by_id: {region_id: [nodes]}
        """
        regions_map = {}
        regions_by_id = {}
        region_graph = {}
        ap_connections = {ap: set() for ap in articulation_points}
        
        visited = set(articulation_points) # Treat APs as boundaries initially
        region_id = 0
        
        height, width = maze.height, maze.width
        
        for r in range(height):
            for c in range(width):
                node = maze.grid[r][c]
                if node.type == '#' or node in visited:
                    continue
                
                # Start New Region
                region_id += 1
                regions_by_id[region_id] = []
                region_graph[region_id] = set()
                
                queue = [node]
                visited.add(node)
                regions_map[node] = region_id
                regions_by_id[region_id].append(node)
                
                while queue:
                    u = queue.pop(0)
                    for v in maze.get_neighbors(u):
                        if v.type == '#': continue
                        
                        if v in articulation_points:
                            ap_connections[v].add(region_id)
                            continue
                            
                        if v not in visited:
                            visited.add(v)
                            regions_map[v] = region_id
                            regions_by_id[region_id].append(v)
                            queue.append(v)
                            
        # Build Graph
        for ap, rids in ap_connections.items():
            rids_list = list(rids)
            for i in range(len(rids_list)):
                for j in range(i+1, len(rids_list)):
                    r1, r2 = rids_list[i], rids_list[j]
                    region_graph[r1].add(r2)
                    region_graph[r2].add(r1)
                    
        return regions_map, region_graph, regions_by_id