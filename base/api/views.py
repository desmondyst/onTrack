from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer

# Show us all the routes in our API
# Only allow GET request
@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]

    # By default only dict is allowed to be serialise
    # we set safe=False to allow the list to be serialise
    return Response(routes)

@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    # serialise more than 1 object
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getRoom(request, pk):
    rooms = Room.objects.get(id=pk)
    # serialise just 1 object
    serializer = RoomSerializer(rooms, many=False)
    return Response(serializer.data)
