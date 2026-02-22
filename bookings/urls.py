from django.urls import path
from .views import book_ticket
from .views import BookTicketView
urlpatterns = [
    path("book-ticket/", book_ticket),
    path('book/', BookTicketView.as_view(), name='book-ticket'),
]
