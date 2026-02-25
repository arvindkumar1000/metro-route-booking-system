from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Ticket, PaymentHistory
from metro.models import Station
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import random


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


# Book Ticket API....
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
        

# Check the detail of ticket...
class TicketDetailView(APIView):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

        data = {
            "success": True,
            "ticket": {
                "ticket_id": ticket.ticket_id,
                "source": ticket.source,
                "destination": ticket.destination,
                "passengers": ticket.passengers,
                "total_fare": ticket.total_fare,
                "stations": ticket.stations,
                "distance": ticket.distance,
                "travel_time": ticket.travel_time,
                "interchanges": ticket.interchanges,
                "booking_time": ticket.booking_time,
                "status": ticket.status,
                "is_used": ticket.is_used,
                "valid_until": ticket.valid_until
            }
        }

        return Response(data)



# Cancel Ticket API here....
class CancelTicketView(APIView):
    def post(self, request):
        ticket_id = request.data.get("ticket_id")

        if not ticket_id:
            return Response(
                {"success": False, "error": "ticket_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

        if ticket.status == "CANCELLED":
            return Response({"success": False, "error": "Ticket already cancelled"})

        ticket.status = "CANCELLED"
        ticket.save()

        return Response({"success": True, "message": "Ticket cancelled"})


# Ticket Validation API (Exist,Expired,Allready Used, Not Canceled)
class ValidateTicketView(APIView):
    def post(self, request):
        ticket_id = request.data.get("ticket_id")

        if not ticket_id:
            return Response(
                {"success": False, "error": "ticket_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        ticket = get_object_or_404(Ticket, ticket_id=ticket_id)

        if ticket.status == "CANCELLED":
            return Response({"success": False, "error": "Ticket cancelled"})

        if ticket.is_used:
            return Response({"success": False, "error": "Ticket already used"})

        if ticket.valid_until < timezone.now():
            return Response({"success": False, "error": "Ticket expired"})

        ticket.is_used = True
        ticket.save()

        return Response({"success": True, "message": "Entry allowed"})


#  Payment API....
class PaymentView(APIView):

    def post(self, request):
        ticket_id = request.data.get("ticket_id")

        if not ticket_id:
            return Response({"success": False, "error": "ticket_id required"})

        try:
            ticket = Ticket.objects.get(ticket_id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({"success": False, "error": "Invalid ticket_id"})

        #  Rule 1 – Only PENDING allowed
        if ticket.status != "PENDING":
            return Response({
                "success": False,
                "error": f"Payment not allowed for status {ticket.status}"
            })

        # Rule 2 – Prevent double success
        already_paid = PaymentHistory.objects.filter(
            ticket=ticket,
            status="SUCCESS"
        ).exists()

        if already_paid:
            return Response({
                "success": False,
                "error": "Payment already completed"
            })

        # Rule 3 – Retry logic
        last_payment = PaymentHistory.objects.filter(ticket=ticket).last()

        if last_payment and last_payment.status == "SUCCESS":
            return Response({
                "success": False,
                "error": "Ticket already paid"
            })

        # Simulated gateway result
        payment_status = random.choice(["SUCCESS", "FAILED"])

        PaymentHistory.objects.create(
            ticket=ticket,
            status=payment_status,
            amount=ticket.total_fare
        )

        # Update ticket
        if payment_status == "SUCCESS":
            ticket.status = "CONFIRMED"
        else:
            ticket.status = "FAILED"

        ticket.save()

        return Response({
            "success": True,
            "payment_status": payment_status,
            "ticket_status": ticket.status
        })

# Add Payment History API...........
class PaymentHistoryView(APIView):
    
    def get(self, request, ticket_id):
        payments = PaymentHistory.objects.filter(ticket__ticket_id=ticket_id).values()

        return Response({
            "success": True,
            "payments": list(payments)
        })