from django.contrib import admin
from .models import PilatesClass, Booking


@admin.register(PilatesClass)
class PilatesClassAdmin(admin.ModelAdmin):
    """Admin interface for PilatesClass model."""

    list_display = ('title', 'instructor', 'date', 'start_time', 'end_time', 'location', 'max_capacity', 'available_spots')
    list_filter = ('date', 'instructor', 'location')
    search_fields = ('title', 'description', 'instructor__email', 'location')
    date_hierarchy = 'date'
    ordering = ('-date', 'start_time')

    fieldsets = (
        ('Class Information', {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'location')
        }),
        ('Capacity', {
            'fields': ('max_capacity',)
        }),
    )

    def available_spots(self, obj):
        """Display available spots."""
        return obj.available_spots
    available_spots.short_description = 'Available Spots'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model."""

    list_display = ('user', 'pilates_class', 'status', 'booked_at')
    list_filter = ('status', 'booked_at', 'pilates_class__date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'pilates_class__title')
    date_hierarchy = 'booked_at'
    ordering = ('-booked_at',)

    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'pilates_class', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )

    readonly_fields = ('booked_at', 'updated_at')
