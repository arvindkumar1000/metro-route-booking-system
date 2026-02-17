from collections import deque
from .models import Connection


def build_graph():
    graph = {}
    
    connections = Connection.objects.select_related("source", "destination")
    
    for conn in connections:
        src = conn.source.code
        dest = conn.destination.code
        
        
        
        graph.setdefault(src, []).append(dest)
        graph.setdefault(dest, []).append(src)
        
    return graph


def bfs_shortest_path(start, goal):
    graph = build_graph()
    
    
    queue = deque([[start]])
    visited = set()
    
    while queue:
        path = queue.popleft()
        node = path[-1]
        
        if node == goal:
            return path
        
        
        if node not in visited:
            visited.add(node)
            
            
            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
            
            
    return None