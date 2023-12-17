from decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Ticket, Distance, PriceRate
from .serializers import TicketSerializer, DistanceSerializer, PriceRateSerializer


class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    @action(detail=False, methods=['GET'])
    def routes(self, request):
        tickets = Ticket.objects.all()
        routes = set((ticket.departure_location, ticket.arrival_location) for ticket in tickets)
        return Response(list(routes))

    @action(detail=True, methods=['PATCH'], url_path='change-price')
    def change_price(self, request, pk=None):
        ticket = self.get_object()
        new_price = request.data.get('new_price')
        if new_price is not None:
            ticket.price = new_price
            ticket.save()
            return Response({'message': 'Price updated successfully'})
        return Response({'error': 'Invalid data'})

    @action(detail=False, methods=['POST'], url_path='add-route')
    def add_route(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            departure_location = data.get('departure_location')
            arrival_location = data.get('arrival_location')

            try:
                distance = Distance.objects.get(departure_location=departure_location,
                                                arrival_location=arrival_location)
            except Distance.DoesNotExist:
                return Response({'error': 'Distance not found for the specified route'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                price_rate = PriceRate.objects.get()
            except PriceRate.DoesNotExist:
                return Response({'error': 'PriceRate not found'}, status=status.HTTP_400_BAD_REQUEST)

            distance_km = distance.distance_km
            rate_per_km = price_rate.rate_per_km
            price = Decimal(distance_km) * rate_per_km

            ticket = Ticket(departure_location=departure_location, arrival_location=arrival_location, distance=distance,
                            price_rate=price_rate, price=price)
            ticket.save()
            return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DistanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Distance.objects.all()
    serializer_class = DistanceSerializer

    # Оставляем только метод POST
    http_method_names = ['post']


class PriceRateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PriceRate.objects.all()
    serializer_class = PriceRateSerializer

    # Оставляем только метод POST
    http_method_names = ['post']
