from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PilatesClassViewSet, BookingViewSet

router = DefaultRouter()
router.register('classes', PilatesClassViewSet, basename='pilatesclass')
router.register('bookings', BookingViewSet, basename='booking')

urlpatterns = router.urls
