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
    path('book/', BookTicketView.as_view(), name='book-ticket'),
    path("pay/", PaymentView.as_view()),
    path("ticket/<uuid:ticket_id>/", TicketDetailView.as_view()),
    path("cancel/", CancelTicketView.as_view()),
    path("validate/", ValidateTicketView.as_view()),
    path("payments/<uuid:ticket_id>/", PaymentHistoryView.as_view()),
    path("refund/", RefundView.as_view()),
    path("admin-stats/", AdminStatsView.as_view()),
]
