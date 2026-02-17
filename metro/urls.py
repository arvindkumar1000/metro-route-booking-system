from django.urls import path
from .views import RouteSearchView


urlpatterns = [
     path("routes/",RouteSearchView.as_view()),
]
