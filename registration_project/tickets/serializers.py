from rest_framework import serializers

from .models import Ticket, Distance, PriceRate


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class DistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distance
        fields = '__all__'


class PriceRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceRate
        fields = '__all__'
