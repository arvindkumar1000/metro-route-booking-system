from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from uuid import UUID
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Ticket, PaymentHistory
from metro.models import Station
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import random
from django.db.models import Sum


# IMPORT SERVICES, NOT VIEWS 
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



# AdminStatsView -(ADMIN ANALYTICS APIs)
class AdminStatsView(APIView):

    def get(self, request):

        total_tickets = Ticket.objects.count()

        confirmed = Ticket.objects.filter(
            status="CONFIRMED"
        ).count()

        pending = Ticket.objects.filter(
            status="PENDING"
        ).count()

        cancelled = Ticket.objects.filter(
            status="CANCELLED"
        ).count()

        failed_payments = PaymentHistory.objects.filter(
            status="FAILED"
        ).count()

        refunded_count = PaymentHistory.objects.filter(
            status="REFUNDED"
        ).count()

        successful_amount = (
            PaymentHistory.objects.filter(
                status="SUCCESS"
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        refunded_amount = (
            PaymentHistory.objects.filter(
                status="REFUNDED"
            ).aggregate(total=Sum("amount"))["total"] or 0
        )

        net_revenue = successful_amount - refunded_amount

        return Response({
            "total_tickets": total_tickets,
            "confirmed_tickets": confirmed,
            "pending_tickets": pending,
            "cancelled_tickets": cancelled,
            "failed_payments": failed_payments,
            "total_refunds": refunded_count,
            "successful_payment_amount": successful_amount,
            "refunded_amount": refunded_amount,
            "net_revenue": net_revenue
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

        #  Validate ticket_id
        if not ticket_id:
            return Response(
                {
                    "success": False,
                    "error": "ticket_id required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ticket_uuid = UUID(str(ticket_id))
        except (ValueError, TypeError, AttributeError):
            return Response(
                {
                    "success": False,
                    "error": "Invalid ticket_id format"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        #  Lock the ticket during cancellation
        with transaction.atomic():

            ticket = (
                Ticket.objects
                .select_for_update()
                .filter(ticket_id=ticket_uuid)
                .first()
            )

            if not ticket:
                return Response(
                    {
                        "success": False,
                        "error": "Ticket not found"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            #  Prevent duplicate cancellation
            if ticket.status == "CANCELLED":
                return Response(
                    {
                        "success": False,
                        "error": "Ticket already cancelled"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Do not cancel a used ticket
            if ticket.is_used:
                return Response(
                    {
                        "success": False,
                        "error": "Used ticket cannot be cancelled"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Reject expired tickets
            if ticket.valid_until <= timezone.now():
                return Response(
                    {
                        "success": False,
                        "error": "Expired ticket cannot be cancelled"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Successful payments must use refund flow
            if ticket.status == "CONFIRMED":
                return Response(
                    {
                        "success": False,
                        "error": (
                            "This ticket is confirmed. "
                            "Use the refund API to process "
                            "cancellation and refund."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Only pending or failed tickets can use
            # this cancellation endpoint
            if ticket.status not in ["PENDING", "FAILED"]:
                return Response(
                    {
                        "success": False,
                        "error": "Ticket cannot be cancelled"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            #  Update ticket status
            ticket.status = "CANCELLED"
            ticket.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Ticket cancelled successfully",
                "ticket_id": str(ticket.ticket_id),
                "ticket_status": ticket.status,
                "refund_status": "NOT_PROCESSED"
            },
            status=status.HTTP_200_OK
        )



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
        
        

#  RefundView API....

from django.core.exceptions import ValidationError

class RefundView(APIView):

    def post(self, request):
        ticket_id = request.data.get("ticket_id")

        # 1. Check required field
        if not ticket_id:
            return Response(
                {
                    "success": False,
                    "error": "ticket_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Validate UUID format
        try:
            ticket_uuid = UUID(str(ticket_id))
        except (ValueError, TypeError, AttributeError):
            return Response(
                {
                    "success": False,
                    "error": "Invalid ticket_id format"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Perform refund updates atomically
        with transaction.atomic():

            ticket = Ticket.objects.select_for_update().filter(
                ticket_id=ticket_uuid
            ).first()

            if not ticket:
                return Response(
                    {
                        "success": False,
                        "error": "Ticket not found"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check refund history BEFORE checking ticket status
            already_refunded = PaymentHistory.objects.filter(
                ticket=ticket,
                status="REFUNDED"
            ).exists()

            if already_refunded:
                return Response(
                    {
                        "success": False,
                        "error": "Already refunded"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 4. Only confirmed tickets are eligible
            if ticket.status != "CONFIRMED":
                return Response(
                    {
                        "success": False,
                        "error": "Refund allowed only for CONFIRMED tickets"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 5. Find successful payment
            payment = PaymentHistory.objects.filter(
                ticket=ticket,
                status="SUCCESS"
            ).order_by("-created_at").first()

            if not payment:
                return Response(
                    {
                        "success": False,
                        "error": "No successful payment found"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 6. Create refund history
            PaymentHistory.objects.create(
                ticket=ticket,
                amount=payment.amount,
                status="REFUNDED"
            )

            # 7. Cancel ticket
            ticket.status = "CANCELLED"
            ticket.save(update_fields=["status"])

        return Response(
            {
                "success": True,
                "message": "Refund successful",
                "ticket_id": str(ticket.ticket_id),
                "ticket_status": ticket.status,
                "refund_amount": payment.amount,
                "refund_status": "REFUNDED"
            },
            status=status.HTTP_200_OK
        )
