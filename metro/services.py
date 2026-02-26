from collections import deque
from .models import Connection, Station


# -----------------------------
# Build Graph
# -----------------------------
def build_graph():
    graph = {}

    connections = Connection.objects.select_related("source", "destination")

    for conn in connections:
        src = conn.source.code
        dest = conn.destination.code

        graph.setdefault(src, []).append(dest)
        graph.setdefault(dest, []).append(src)

    return graph


# -----------------------------
# Calculate Distance
# -----------------------------
def calculate_distance(path):
    total_distance = 0

    for i in range(len(path) - 1):
        try:
            conn = Connection.objects.get(
                source__code=path[i],
                destination__code=path[i + 1]
            )
        except Connection.DoesNotExist:
            conn = Connection.objects.get(
                source__code=path[i + 1],
                destination__code=path[i]
            )

        total_distance += conn.distance

    return total_distance


# -----------------------------
# Fare Calculation (Rs. Logic)
# -----------------------------
def calculate_fare(distance):
    if distance <= 2:
        return 10
    elif distance <= 5:
        return 20
    elif distance <= 12:
        return 30
    else:
        return 40


# -----------------------------
# BFS Shortest Path
# -----------------------------
def bfs_shortest_path(start, goal):
    graph = build_graph()

    queue = deque([[start]])
    visited = set()

    while queue:
        path = queue.popleft()
        node = path[-1]

        if node == goal:
            return path   # ONLY LIST RETURN

        if node not in visited:
            visited.add(node)

            for neighbor in graph.get(node, []):
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)

    return None

#  claculate Interchange
def calculate_interchanges(path):
    interchanges = 0

    for i in range(len(path) - 1):

        current_station = Station.objects.get(code=path[i])
        next_station = Station.objects.get(code=path[i + 1])

        if current_station.line != next_station.line:
            interchanges += 1

    return interchanges

# calculate travel time
def calculate_travel_time(path, interchanges):
    
    stations_count = len(path) - 1

    travel_time = (stations_count * 2) + (interchanges * 5)

    return travel_time
