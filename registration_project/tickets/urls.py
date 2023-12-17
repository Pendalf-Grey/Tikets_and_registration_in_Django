from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, DistanceViewSet, PriceRateViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)
router.register(r'distances', DistanceViewSet)
router.register(r'pricerates', PriceRateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]