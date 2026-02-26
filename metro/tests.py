from django.test import TestCase
from rest_framework.test import APIClient
from .models import Station, Connection
from .services import (
    build_graph,
    bfs_shortest_path,
    calculate_distance,
    calculate_fare,
    calculate_interchanges,
    calculate_travel_time
)

# Create your tests here.

class MetroServiceTests(TestCase):

    def setUp(self):
        """
        Graph Layout:

        A (Red) —— B (Red) —— C (Blue) —— D (Blue)

        Distances:
        A-B = 2
        B-C = 3
        C-D = 4
        """

        self.a = Station.objects.create(name="Station A", code="A", line="Red")
        self.b = Station.objects.create(name="Station B", code="B", line="Red")
        self.c = Station.objects.create(name="Station C", code="C", line="Blue")
        self.d = Station.objects.create(name="Station D", code="D", line="Blue")

        Connection.objects.create(source=self.a, destination=self.b, distance=2)
        Connection.objects.create(source=self.b, destination=self.c, distance=3)
        Connection.objects.create(source=self.c, destination=self.d, distance=4)

    # -----------------------------
    # Graph Tests
    # -----------------------------
    def test_build_graph(self):
        graph = build_graph()

        self.assertIn("A", graph)
        self.assertIn("B", graph)
        self.assertIn("C", graph)

        self.assertIn("B", graph["A"])
        self.assertIn("A", graph["B"])

    # -----------------------------
    # BFS Tests
    # -----------------------------
    def test_bfs_shortest_path(self):
        path = bfs_shortest_path("A", "D")

        self.assertEqual(path, ["A", "B", "C", "D"])

    def test_bfs_no_route(self):
        Station.objects.create(name="Isolated", code="X", line="Green")

        path = bfs_shortest_path("A", "X")

        self.assertIsNone(path)

    # -----------------------------
    # Distance Tests
    # -----------------------------
    def test_calculate_distance(self):
        path = ["A", "B", "C"]

        distance = calculate_distance(path)

        self.assertEqual(distance, 5)  # 2 + 3

    # -----------------------------
    # Fare Tests
    # -----------------------------
    def test_calculate_fare(self):
        self.assertEqual(calculate_fare(1), 10)
        self.assertEqual(calculate_fare(4), 20)
        self.assertEqual(calculate_fare(10), 30)
        self.assertEqual(calculate_fare(20), 40)

    # -----------------------------
    # Interchange Tests
    # -----------------------------
    def test_interchanges(self):
        path = ["A", "B", "C", "D"]

        interchanges = calculate_interchanges(path)

        self.assertEqual(interchanges, 1)  # Red → Blue

    # -----------------------------
    # Travel Time Tests
    # -----------------------------
    def test_travel_time(self):
        path = ["A", "B", "C", "D"]
        interchanges = 1

        time = calculate_travel_time(path, interchanges)

        # stations_count = 3 → 3*2 = 6
        # interchanges = 1 → 1*5 = 5
        # total = 11
        self.assertEqual(time, 11)


class RouteSearchAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.a = Station.objects.create(name="Station A", code="A", line="Red")
        self.b = Station.objects.create(name="Station B", code="B", line="Red")

        Connection.objects.create(source=self.a, destination=self.b, distance=2)

    def test_route_search_success(self):
        response = self.client.get("/api/metro/route/?source=A&destination=B")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["fare"], 10)

    def test_route_search_missing_params(self):
        response = self.client.get("/api/metro/route/")

        self.assertEqual(response.status_code, 400)

    def test_route_search_same_station(self):
        response = self.client.get("/api/metro/route/?source=A&destination=A")

        self.assertEqual(response.status_code, 400)

    def test_route_search_no_route(self):
        Station.objects.create(name="X", code="X", line="Blue")

        response = self.client.get("/api/metro/route/?source=A&destination=X")

        self.assertEqual(response.status_code, 404)