from django.urls import path
from .views import RouteSearchView

urlpatterns = [
    path("route/", RouteSearchView.as_view()), 
]
