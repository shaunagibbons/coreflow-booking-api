from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class PilatesClass(models.Model):
    """Model representing a Pilates class."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='classes_teaching',
        limit_choices_to={'is_instructor': True}
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_capacity = models.PositiveIntegerField(default=10)
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pilates Class'
        verbose_name_plural = 'Pilates Classes'
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['date', 'start_time']),
            models.Index(fields=['instructor']),
        ]

    def __str__(self):
        return f"{self.title} - {self.date} at {self.start_time}"

    def clean(self):
        """Validate that end_time is after start_time."""
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({
                'end_time': 'End time must be after start time.'
            })

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_full(self):
        """Check if the class has reached maximum capacity."""
        return self.bookings.filter(status='confirmed').count() >= self.max_capacity

    @property
    def available_spots(self):
        """Return the number of available spots."""
        confirmed_bookings = self.bookings.filter(status='confirmed').count()
        return max(0, self.max_capacity - confirmed_bookings)

    @property
    def datetime_start(self):
        """Combine date and start_time into a single datetime object."""
        from datetime import datetime
        return timezone.make_aware(
            datetime.combine(self.date, self.start_time)
        )

    def get_cutoff_time(self, hours_before=2):
        """Get the cutoff time for booking (default 2 hours before class)."""
        return self.datetime_start - timedelta(hours=hours_before)

    def can_book(self):
        """Check if the class can be booked (not full and before cutoff)."""
        return not self.is_full and timezone.now() < self.get_cutoff_time()


class Booking(models.Model):
    """Model representing a booking for a Pilates class."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    pilates_class = models.ForeignKey(
        PilatesClass,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-booked_at']
        unique_together = ['user', 'pilates_class']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['pilates_class', 'status']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.pilates_class.title} ({self.status})"

    def clean(self):
        """Validate booking constraints."""
        # Check if class is full (only for confirmed bookings)
        if self.status == 'confirmed' and self.pilates_class.is_full:
            # Allow if this booking already exists (update case)
            if not self.pk:
                raise ValidationError('This class is already full.')

        # Check cutoff time for new bookings
        if not self.pk and timezone.now() >= self.pilates_class.get_cutoff_time():
            raise ValidationError(
                'Booking cutoff time has passed. You can no longer book this class.'
            )

    def save(self, *args, **kwargs):
        """Override save to call full_clean."""
        self.full_clean()
        super().save(*args, **kwargs)

    def can_cancel(self, hours_before=2):
        """Check if the booking can be cancelled (before cutoff time)."""
        if self.status == 'cancelled':
            return False
        return timezone.now() < self.pilates_class.get_cutoff_time(hours_before)

    def cancel(self):
        """Cancel the booking if allowed."""
        if not self.can_cancel():
            raise ValidationError('Cannot cancel booking after cutoff time.')
        self.status = 'cancelled'
        self.save()
