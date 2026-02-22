from django.urls import path
from .views import book_ticket
from .views import (
    BookTicketView,
    TicketDetailView,
    CancelTicketView,
    ValidateTicketView
    )
urlpatterns = [
    path("book-ticket/", book_ticket),
    path('book/', BookTicketView.as_view(), name='book-ticket'),
    path("ticket/<uuid:ticket_id>/", TicketDetailView.as_view()),
    path("cancel/", CancelTicketView.as_view()),
    path("validate/", ValidateTicketView.as_view()),
]
