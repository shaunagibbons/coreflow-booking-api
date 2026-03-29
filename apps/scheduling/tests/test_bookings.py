import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from datetime import date, time, timedelta
from apps.scheduling.models import PilatesClass, Booking


@pytest.mark.django_db
class TestBookingEndpoints:
    """Tests for booking API endpoints."""

    @pytest.fixture
    def future_class(self, instructor):
        """Create a class in the future."""
        return PilatesClass.objects.create(
            title='Test Class',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(14, 0),
            end_time=time(15, 0),
            max_capacity=10,
            location='Studio A'
        )

    def test_create_booking(self, authenticated_client, future_class):
        """Test creating a booking."""
        url = reverse('booking-list')
        data = {
            'pilates_class': future_class.id,
            'notes': 'Looking forward to it!'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Booking.objects.count() == 1

    def test_list_bookings(self, authenticated_client, user, future_class):
        """Test listing bookings."""
        Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )

        url = reverse('booking-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_get_upcoming_bookings(self, authenticated_client, user, instructor):
        """Test getting upcoming bookings."""
        # Create future class and booking
        future_class = PilatesClass.objects.create(
            title='Future Class',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(14, 0),
            end_time=time(15, 0),
            max_capacity=10,
            location='Studio A'
        )
        Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )

        # Create past class and booking (bypass validation for test data)
        past_class = PilatesClass.objects.create(
            title='Past Class',
            instructor=instructor,
            date=date.today() - timedelta(days=7),
            start_time=time(14, 0),
            end_time=time(15, 0),
            max_capacity=10,
            location='Studio A'
        )
        past_booking = Booking(
            user=user,
            pilates_class=past_class,
            status='confirmed',
            booked_at=timezone.now() - timedelta(days=7),
            updated_at=timezone.now() - timedelta(days=7),
        )
        past_booking.save_base(raw=True)

        url = reverse('booking-upcoming')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['pilates_class_title'] == 'Future Class'

    def test_cancel_booking(self, authenticated_client, user, future_class):
        """Test cancelling a booking."""
        booking = Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )

        url = reverse('booking-cancel', kwargs={'pk': booking.id})
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK

        booking.refresh_from_db()
        assert booking.status == 'cancelled'

    def test_unauthenticated_cannot_create_booking(self, api_client, future_class):
        """Test that unauthenticated users cannot create bookings."""
        url = reverse('booking-list')
        data = {'pilates_class': future_class.id}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestClassEndpoints:
    """Tests for class API endpoints."""

    def test_list_classes(self, authenticated_client, instructor):
        """Test listing Pilates classes."""
        PilatesClass.objects.create(
            title='Morning Class',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=10,
            location='Studio A'
        )

        url = reverse('pilatesclass-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_filter_classes_by_date(self, authenticated_client, instructor):
        """Test filtering classes by date range."""
        today = date.today()
        PilatesClass.objects.create(
            title='Today Class',
            instructor=instructor,
            date=today,
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=10,
            location='Studio A'
        )
        PilatesClass.objects.create(
            title='Future Class',
            instructor=instructor,
            date=today + timedelta(days=14),
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=10,
            location='Studio A'
        )

        url = reverse('pilatesclass-list')
        response = authenticated_client.get(url, {'date_from': today, 'date_to': today})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_instructor_can_create_class(self, api_client, instructor):
        """Test that instructors can create classes."""
        api_client.force_authenticate(user=instructor)
        url = reverse('pilatesclass-list')
        data = {
            'title': 'New Class',
            'description': 'A great class',
            'instructor_id': instructor.id,
            'date': str(date.today() + timedelta(days=7)),
            'start_time': '09:00:00',
            'end_time': '10:00:00',
            'max_capacity': 10,
            'location': 'Studio A'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_regular_user_cannot_create_class(self, authenticated_client):
        """Test that regular users cannot create classes."""
        url = reverse('pilatesclass-list')
        data = {
            'title': 'New Class',
            'date': str(date.today() + timedelta(days=7)),
            'start_time': '09:00:00',
            'end_time': '10:00:00',
            'max_capacity': 10,
            'location': 'Studio A'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
