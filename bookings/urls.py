from django.urls import path
from .views import book_ticket
from .views import (
    BookTicketView,
    TicketDetailView,
    CancelTicketView,
    ValidateTicketView,
    RefundView,
    PaymentView,
    PaymentHistoryView,
    AdminStatsView,
    )
urlpatterns = [
    path("book-ticket/", book_ticket),
    path('book/', BookTicketView.as_view(),name="book-ticket"),
    path("pay/", PaymentView.as_view(),name="payment"),
    path("ticket/<uuid:ticket_id>/", TicketDetailView.as_view(),name="ticket-detail"),
    path("cancel/", CancelTicketView.as_view(), name="cancel-ticket"),
    path("validate/", ValidateTicketView.as_view(),name="validate-ticket"),
    path("payments/<uuid:ticket_id>/", PaymentHistoryView.as_view(),name="payment-history"),
    path("refund/", RefundView.as_view(),name="refund"),
    path("admin-stats/", AdminStatsView.as_view(),name="admin-stats"),
]
