from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import PilatesClass, Booking
from .serializers import (
    PilatesClassSerializer,
    BookingSerializer,
    BookingCreateSerializer,
    BookingListSerializer
)


class IsInstructorOrReadOnly(permissions.BasePermission):
    """Custom permission to allow instructors to create/edit classes."""

    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for authenticated instructors or staff
        return (request.user and request.user.is_authenticated
                and (request.user.is_instructor or request.user.is_staff))

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the instructor who created it or staff
        return obj.instructor == request.user or request.user.is_staff


class PilatesClassViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Pilates classes."""

    queryset = PilatesClass.objects.select_related('instructor').all()
    serializer_class = PilatesClassSerializer
    permission_classes = [IsInstructorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'location', 'instructor__first_name', 'instructor__last_name']
    ordering_fields = ['date', 'start_time', 'created_at']
    ordering = ['date', 'start_time']

    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        # Filter by instructor
        instructor_id = self.request.query_params.get('instructor')
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)

        # Filter by location
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by availability
        available_only = self.request.query_params.get('available_only')
        if available_only == 'true':
            # This is a simplified filter - for better performance, consider annotating
            queryset = [cls for cls in queryset if cls.can_book()]
            return queryset

        return queryset

    def perform_create(self, serializer):
        """Set the instructor to the current user if they're an instructor."""
        if self.request.user.is_instructor:
            serializer.save(instructor=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Get all bookings for a specific class."""
        pilates_class = self.get_object()

        # Only instructor of the class or staff can see bookings
        if pilates_class.instructor != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not have permission to view these bookings.'},
                status=status.HTTP_403_FORBIDDEN
            )

        bookings = pilates_class.bookings.filter(status='confirmed')
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing bookings."""

    queryset = Booking.objects.select_related('user', 'pilates_class', 'pilates_class__instructor').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'list':
            return BookingListSerializer
        return BookingSerializer

    def get_queryset(self):
        """Return bookings for the current user only."""
        # Staff can see all bookings, regular users see only their own
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create booking for the authenticated user and send confirmation email."""
        booking = serializer.save(user=self.request.user)
        send_mail(
            subject=f'Booking Confirmed: {booking.pilates_class.title}',
            message=(
                f'Hi {booking.user.first_name},\n\n'
                f'Your booking for {booking.pilates_class.title} on '
                f'{booking.pilates_class.date} at {booking.pilates_class.start_time} '
                f'has been confirmed.\n\n'
                f'Location: {booking.pilates_class.location}\n'
                f'Instructor: {booking.pilates_class.instructor.get_full_name()}\n\n'
                f'Thank you,\nCoreflow Pilates'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            fail_silently=False,
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking."""
        booking = self.get_object()

        # Check if user owns this booking
        if booking.user != request.user and not request.user.is_staff:
            return Response(
                {'detail': 'You do not have permission to cancel this booking.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if booking can be cancelled
        if not booking.can_cancel():
            return Response(
                {'detail': 'Cannot cancel booking. Cutoff time has passed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cancel the booking
        booking.status = 'cancelled'
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings for the current user."""
        upcoming_bookings = self.get_queryset().filter(
            status='confirmed',
            pilates_class__date__gte=timezone.now().date()
        ).order_by('pilates_class__date', 'pilates_class__start_time')

        serializer = BookingListSerializer(upcoming_bookings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def past(self, request):
        """Get past bookings for the current user."""
        past_bookings = self.get_queryset().filter(
            pilates_class__date__lt=timezone.now().date()
        ).order_by('-pilates_class__date', '-pilates_class__start_time')

        serializer = BookingListSerializer(past_bookings, many=True)
        return Response(serializer.data)
