import pytest
from django.urls import reverse
from rest_framework import status
from datetime import date, time, timedelta
from apps.scheduling.models import PilatesClass, Booking


@pytest.mark.django_db
class TestBookingValidation:
    """Tests for booking validation and business rules."""

    @pytest.fixture
    def future_class(self, instructor):
        """Create a class in the future."""
        return PilatesClass.objects.create(
            title='Test Class',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(14, 0),
            end_time=time(15, 0),
            max_capacity=2,
            location='Studio A'
        )

    def test_cannot_book_full_class(self, authenticated_client, user, future_class):
        """Test that booking a full class is prevented."""
        # Create another user and fill the class
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user1 = User.objects.create_user(email='user1@example.com', password='pass')
        user2 = User.objects.create_user(email='user2@example.com', password='pass')

        Booking.objects.create(user=user1, pilates_class=future_class, status='confirmed')
        Booking.objects.create(user=user2, pilates_class=future_class, status='confirmed')

        # Try to book the full class
        url = reverse('booking-list')
        data = {'pilates_class': future_class.id}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'full' in str(response.data).lower()

    def test_cannot_double_book(self, authenticated_client, user, future_class):
        """Test that double booking is prevented."""
        # Create first booking
        Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )

        # Try to book the same class again
        url = reverse('booking-list')
        data = {'pilates_class': future_class.id}
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already have a booking' in str(response.data).lower()

    def test_can_cancel_booking_before_cutoff(self, authenticated_client, user, future_class):
        """Test that bookings can be cancelled before cutoff time."""
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

    def test_user_can_only_see_own_bookings(self, authenticated_client, user, future_class):
        """Test that users can only see their own bookings."""
        # Create booking for authenticated user
        booking1 = Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )

        # Create booking for another user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other_user = User.objects.create_user(
            email='other@example.com',
            password='pass',
            first_name='Other',
            last_name='User'
        )
        booking2 = Booking.objects.create(
            user=other_user,
            pilates_class=future_class,
            status='confirmed'
        )

        url = reverse('booking-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == booking1.id
