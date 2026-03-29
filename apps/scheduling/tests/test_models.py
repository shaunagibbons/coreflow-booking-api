import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, time, timedelta
from apps.scheduling.models import PilatesClass, Booking


@pytest.mark.django_db
class TestPilatesClassModel:
    """Tests for PilatesClass model."""

    def test_create_pilates_class(self, instructor):
        """Test creating a Pilates class."""
        pilates_class = PilatesClass.objects.create(
            title='Morning Pilates',
            description='A relaxing morning session',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=10,
            location='Studio A'
        )
        assert pilates_class.title == 'Morning Pilates'
        assert pilates_class.instructor == instructor
        assert pilates_class.max_capacity == 10

    def test_pilates_class_str_representation(self, instructor):
        """Test string representation of PilatesClass."""
        pilates_class = PilatesClass.objects.create(
            title='Morning Pilates',
            instructor=instructor,
            date=date(2026, 3, 15),
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=10,
            location='Studio A'
        )
        expected = 'Morning Pilates - 2026-03-15 at 09:00:00'
        assert str(pilates_class) == expected

    def test_end_time_before_start_time_raises_error(self, instructor):
        """Test that end_time before start_time raises ValidationError."""
        with pytest.raises(ValidationError):
            pilates_class = PilatesClass(
                title='Invalid Class',
                instructor=instructor,
                date=date.today() + timedelta(days=7),
                start_time=time(10, 0),
                end_time=time(9, 0),
                max_capacity=10,
                location='Studio A'
            )
            pilates_class.save()

    def test_available_spots_calculation(self, instructor, user):
        """Test available spots calculation."""
        pilates_class = PilatesClass.objects.create(
            title='Morning Pilates',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=10,
            location='Studio A'
        )
        assert pilates_class.available_spots == 10

        # Create a booking
        Booking.objects.create(
            user=user,
            pilates_class=pilates_class,
            status='confirmed'
        )
        assert pilates_class.available_spots == 9

    def test_is_full_property(self, instructor, user):
        """Test is_full property."""
        pilates_class = PilatesClass.objects.create(
            title='Small Class',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(9, 0),
            end_time=time(10, 0),
            max_capacity=1,
            location='Studio A'
        )
        assert not pilates_class.is_full

        # Fill the class
        Booking.objects.create(
            user=user,
            pilates_class=pilates_class,
            status='confirmed'
        )
        assert pilates_class.is_full


@pytest.mark.django_db
class TestBookingModel:
    """Tests for Booking model."""

    @pytest.fixture
    def future_class(self, instructor):
        """Create a class in the future."""
        return PilatesClass.objects.create(
            title='Future Class',
            instructor=instructor,
            date=date.today() + timedelta(days=7),
            start_time=time(14, 0),
            end_time=time(15, 0),
            max_capacity=10,
            location='Studio A'
        )

    def test_create_booking(self, user, future_class):
        """Test creating a booking."""
        booking = Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )
        assert booking.user == user
        assert booking.pilates_class == future_class
        assert booking.status == 'confirmed'

    def test_booking_str_representation(self, user, future_class):
        """Test string representation of Booking."""
        booking = Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )
        expected = f"{user.get_full_name()} - {future_class.title} (confirmed)"
        assert str(booking) == expected

    def test_cannot_create_duplicate_booking(self, user, future_class):
        """Test that duplicate bookings are prevented."""
        Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )

        with pytest.raises(Exception):  # IntegrityError or ValidationError
            Booking.objects.create(
                user=user,
                pilates_class=future_class,
                status='confirmed'
            )

    def test_can_cancel_booking(self, user, future_class):
        """Test can_cancel method."""
        booking = Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='confirmed'
        )
        # Future class should be cancellable
        assert booking.can_cancel()

    def test_cancelled_booking_cannot_be_cancelled_again(self, user, future_class):
        """Test that cancelled bookings cannot be cancelled again."""
        booking = Booking.objects.create(
            user=user,
            pilates_class=future_class,
            status='cancelled'
        )
        assert not booking.can_cancel()
