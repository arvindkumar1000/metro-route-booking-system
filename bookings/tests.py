from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from bookings.models import Ticket, PaymentHistory
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

# Create your tests here.

class BookingTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.ticket = Ticket.objects.create(
            source="A",
            destination="B",
            passengers=1,
            fare_per_person=10,
            total_fare=10,
            stations=["A", "B"],
            distance=1,
            interchanges=0,
            travel_time=5,
            valid_until=timezone.now() + timedelta(minutes=30),
            status="PENDING"
        )

    def test_ticket_detail(self):
        url = reverse("ticket-detail", args=[self.ticket.ticket_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    def test_cancel_ticket(self):
        url = reverse("cancel-ticket")
        response = self.client.post(url, {"ticket_id": self.ticket.ticket_id})

        self.ticket.refresh_from_db()
        self.assertTrue(response.data["success"])
        self.assertEqual(self.ticket.status, "CANCELLED")

    def test_validate_ticket_success(self):
        url = reverse("validate-ticket")
        response = self.client.post(url, {"ticket_id": self.ticket.ticket_id})

        self.ticket.refresh_from_db()
        self.assertTrue(response.data["success"])
        self.assertTrue(self.ticket.is_used)

    def test_validate_expired_ticket(self):
        self.ticket.valid_until = timezone.now() - timedelta(minutes=1)
        self.ticket.save()

        url = reverse("validate-ticket")
        response = self.client.post(url, {"ticket_id": self.ticket.ticket_id})

        self.assertFalse(response.data["success"])

    @patch("bookings.views.random.choice", return_value="SUCCESS")
    def test_payment_success(self, mocked):
        url = reverse("payment")
        response = self.client.post(url, {"ticket_id": self.ticket.ticket_id})

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "CONFIRMED")

    @patch("bookings.views.random.choice", return_value="FAILED")
    def test_payment_failed(self, mocked):
        url = reverse("payment")
        response = self.client.post(url, {"ticket_id": self.ticket.ticket_id})

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, "FAILED")

    def test_admin_stats(self):
        PaymentHistory.objects.create(
            ticket=self.ticket,
            amount=10,
            status="SUCCESS"
        )

        url = reverse("admin-stats")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("revenue", response.data)