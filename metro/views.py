from rest_framework.views import APIView
from rest_framework.response import Response
from .services import (
    bfs_shortest_path,
    calculate_interchanges,
    calculate_fare,
    calculate_distance,
    calculate_travel_time

)
from .models import Station




# Create your views here.


class RouteSearchView(APIView):

    def get(self, request):
        source = request.GET.get("source")
        destination = request.GET.get("destination")

        #  Validate input
        if not source or not destination:
            return Response(
                {"success": False, "error": "source and destination required"},
                status=400
            )

        if source == destination:
            return Response(
                {"success": False, "error": "Source and destination cannot be same"},
                status=400
            )

        #  BFS
        path = bfs_shortest_path(source, destination)

        if not path:
            return Response(
                {"success": False, "error": "No route found"},
                status=404
            )

        #  Convert codes → names
        station_names = []
        for code in path:
            station = Station.objects.get(code=code)
            station_names.append(station.name)

        #  Calculations
        interchanges = calculate_interchanges(path)
        total_distance = calculate_distance(path)
        fare = calculate_fare(total_distance)
        travel_time = calculate_travel_time(path, interchanges)


        return Response({
            "success": True,
            "stations": station_names,
            "distance": total_distance,
            "fare": fare,
            "interchanges": interchanges,
            "travel_time": travel_time

        })