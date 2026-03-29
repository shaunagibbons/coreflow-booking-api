from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import PilatesClass, Booking

User = get_user_model()


class InstructorSerializer(serializers.ModelSerializer):
    """Nested serializer for instructor information."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name')
        read_only_fields = fields


class InstructorPrimaryKeyField(serializers.PrimaryKeyRelatedField):
    """Lazy queryset field that filters to instructors only."""

    def get_queryset(self):
        return User.objects.filter(is_instructor=True)


class PilatesClassSerializer(serializers.ModelSerializer):
    """Serializer for PilatesClass model."""

    instructor = InstructorSerializer(read_only=True)
    instructor_id = InstructorPrimaryKeyField(
        source='instructor',
        write_only=True
    )
    available_spots = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    can_book = serializers.SerializerMethodField()

    class Meta:
        model = PilatesClass
        fields = (
            'id', 'title', 'description', 'instructor', 'instructor_id',
            'date', 'start_time', 'end_time', 'max_capacity', 'location',
            'available_spots', 'is_full', 'can_book',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_can_book(self, obj):
        """Check if the class can be booked."""
        return obj.can_book()

    def validate(self, attrs):
        """Validate class data."""
        # Validate that end_time is after start_time
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })

        # Validate that instructor is actually an instructor
        instructor = attrs.get('instructor')
        if instructor and not instructor.is_instructor:
            raise serializers.ValidationError({
                'instructor': 'Selected user is not an instructor.'
            })

        return attrs


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model (read operations)."""

    user = serializers.StringRelatedField(read_only=True)
    pilates_class = PilatesClassSerializer(read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id', 'user', 'pilates_class', 'status',
            'booked_at', 'updated_at', 'notes', 'can_cancel'
        )
        read_only_fields = ('id', 'booked_at', 'updated_at')

    def get_can_cancel(self, obj):
        """Check if the booking can be cancelled."""
        return obj.can_cancel()


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings with validation."""

    class Meta:
        model = Booking
        fields = ('pilates_class', 'notes')

    def validate_pilates_class(self, value):
        """Validate that the class can be booked."""
        # Check if class is full
        if value.is_full:
            raise serializers.ValidationError('This class is already full.')

        # Check cutoff time
        cutoff_time = value.get_cutoff_time()
        if timezone.now() >= cutoff_time:
            raise serializers.ValidationError(
                f'Booking cutoff time has passed. Bookings must be made at least 2 hours before the class.'
            )

        # Check if user already has a booking for this class
        user = self.context['request'].user
        existing_booking = Booking.objects.filter(
            user=user,
            pilates_class=value,
            status__in=['confirmed', 'pending']
        ).exists()

        if existing_booking:
            raise serializers.ValidationError(
                'You already have a booking for this class.'
            )

        return value

    def create(self, validated_data):
        """Create booking with authenticated user."""
        validated_data['user'] = self.context['request'].user
        validated_data['status'] = 'confirmed'
        return super().create(validated_data)


class BookingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for booking lists."""

    pilates_class_title = serializers.CharField(source='pilates_class.title', read_only=True)
    pilates_class_date = serializers.DateField(source='pilates_class.date', read_only=True)
    pilates_class_time = serializers.TimeField(source='pilates_class.start_time', read_only=True)
    instructor_name = serializers.CharField(source='pilates_class.instructor.get_full_name', read_only=True)
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id', 'pilates_class', 'pilates_class_title', 'pilates_class_date',
            'pilates_class_time', 'instructor_name', 'status',
            'booked_at', 'can_cancel'
        )

    def get_can_cancel(self, obj):
        """Check if the booking can be cancelled."""
        return obj.can_cancel()
