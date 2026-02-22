from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Ticket
from django.utils import timezone
from datetime import timedelta
from .models import Ticket
from metro.models import Station
from rest_framework.views import APIView
from rest_framework.response import Response


# IMPORT SERVICES, NOT VIEWS ✅
from metro.services import (
    bfs_shortest_path,
    calculate_interchanges,
    calculate_fare,
    calculate_distance,
    calculate_travel_time
)


@api_view(["POST"])
def book_ticket(request):
    source = request.data.get("source")
    destination = request.data.get("destination")
    passengers = int(request.data.get("passengers", 1))

    if not source or not destination:
        return Response({"error": "Missing stations"}, status=400)

    if source == destination:
        return Response({"error": "Invalid stations"}, status=400)

    # BFS
    path = bfs_shortest_path(source, destination)

    if not path:
        return Response({"error": "No route found"}, status=404)

    # Convert codes → names
    station_names = []
    for code in path:
        station = Station.objects.get(code=code)
        station_names.append(station.name)

    # Calculations
    interchanges = calculate_interchanges(path)
    total_distance = calculate_distance(path)
    fare = calculate_fare(total_distance)
    travel_time = calculate_travel_time(path, interchanges)

    total_fare = fare * passengers

    ticket = Ticket.objects.create(
        source=source,
        destination=destination,
        passengers=passengers,
        fare_per_person=fare,
        total_fare=total_fare,
        stations=station_names,
        distance=total_distance,
        interchanges=interchanges,
        travel_time=travel_time
    )

    return Response({
        "success": True,
        "ticket_id": ticket.ticket_id,
        "stations": station_names,
        "total_fare": total_fare
    })



class BookTicketView(APIView):

    def post(self, request):
        source = request.data.get("source")
        destination = request.data.get("destination")
        passengers = int(request.data.get("passengers", 1))

        path = bfs_shortest_path(source, destination)

        if not path:
            return Response({"success": False, "error": "No route found"}, status=404)

        interchanges = calculate_interchanges(path)
        distance = calculate_distance(path)
        fare_per_person = calculate_fare(distance)
        travel_time = calculate_travel_time(path, interchanges)

        total_fare = fare_per_person * passengers

        valid_until = timezone.now() + timedelta(minutes=travel_time + 15)

        ticket = Ticket.objects.create(
            source=source,
            destination=destination,
            passengers=passengers,
            fare_per_person=fare_per_person,
            total_fare=total_fare,
            stations=path,
            distance=distance,
            interchanges=interchanges,
            travel_time=travel_time,
            valid_until=valid_until
        )
        

        print("SOURCE =", source)
        print("DESTINATION =", destination)
        print("AVAILABLE STATIONS =", list(Station.objects.values_list("name", flat=True)))

        return Response({
            "success": True,
            "ticket_id": ticket.ticket_id,
            "total_fare": total_fare,
            "valid_until": valid_until
        })
        





class ValidateTicketView(APIView):
    
    def get(self, request):
        ticket_id = request.GET.get("ticket_id")

        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({"valid": False, "reason": "INVALID_TICKET"})

        if ticket.status != "CONFIRMED":
            return Response({"valid": False, "reason": "CANCELLED"})

        if ticket.is_used:
            return Response({"valid": False, "reason": "ALREADY_USED"})

        if timezone.now() > ticket.valid_until:
            return Response({"valid": False, "reason": "EXPIRED"})

        ticket.is_used = True
        ticket.save()

        return Response({"valid": True})


