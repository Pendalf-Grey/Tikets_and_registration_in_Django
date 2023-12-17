from decimal import Decimal

from django.db import models


class Distance(models.Model):
    departure_city = models.CharField(max_length=100, help_text="Город отправления")
    arrival_city = models.CharField(max_length=100, help_text="Город прибытия")
    distance_km = models.PositiveIntegerField(help_text="Расстояние в километрах")


class PriceRate(models.Model):
    rate_per_km = models.DecimalField(max_digits=5, decimal_places=2, help_text="Цена за 1 км")


class Ticket(models.Model):
    airline = models.CharField(max_length=100, help_text="Авиакомпания")
    departure_location = models.CharField(max_length=100, help_text="Место отправления")
    arrival_location = models.CharField(max_length=100, help_text="Место прибытия")
    departure_datetime = models.DateTimeField(help_text="Дата и время вылета")
    available_seats = models.PositiveIntegerField(help_text="Количество доступных мест")
    description = models.TextField(help_text="Дополнительная информация")
    distance = models.ForeignKey(Distance, on_delete=models.CASCADE)
    price_rate = models.ForeignKey(PriceRate, on_delete=models.CASCADE)

    def calculate_price(self):

        distance_km = self.distance.distance_km
        rate_per_km = self.price_rate.rate_per_km

        price = Decimal(distance_km) * rate_per_km
        self.price = price
        self.save()
