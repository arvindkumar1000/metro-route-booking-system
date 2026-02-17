from rest_framework.views import APIView
from rest_framework.response import Response
from .services import bfs_shortest_path

# Create your views here.

class RouteSearchView(APIView):
    def get(self, request):
        source = request.GET.get("source")
        destination = request.GET.get("destination")
        
        
        if not source or not destination:
            return Response({"error": "source and destination required"},status=400)
        
        path = bfs_shortest_path(source, destination)
        
        return Response({
            "route": path
        })