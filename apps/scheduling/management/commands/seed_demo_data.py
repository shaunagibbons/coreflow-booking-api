"""
Management command to seed the database with demo data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, time
from apps.scheduling.models import PilatesClass, Booking

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with demo data for Pilates booking system'

    def handle(self, *args, **options):
        self.stdout.write('Seeding demo data...\n')

        # --- Instructors ---
        instructors_data = [
            {
                'email': 'sarah.mitchell@coreflow.com',
                'password': 'Demo1234!',
                'first_name': 'Sarah',
                'last_name': 'Mitchell',
                'phone_number': '+353 87 123 4567',
                'is_instructor': True,
            },
            {
                'email': 'james.brennan@coreflow.com',
                'password': 'Demo1234!',
                'first_name': 'James',
                'last_name': 'Brennan',
                'phone_number': '+353 86 234 5678',
                'is_instructor': True,
            },
            {
                'email': 'emma.walsh@coreflow.com',
                'password': 'Demo1234!',
                'first_name': 'Emma',
                'last_name': 'Walsh',
                'phone_number': '+353 85 345 6789',
                'is_instructor': True,
            },
        ]

        instructors = []
        for data in instructors_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults=data,
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(f'  Created instructor: {user.get_full_name()}')
            else:
                self.stdout.write(f'  Instructor already exists: {user.get_full_name()}')
            instructors.append(user)

        sarah, james, emma = instructors

        # --- Regular Members ---
        members_data = [
            {
                'email': 'olivia.kelly@example.com',
                'password': 'Demo1234!',
                'first_name': 'Olivia',
                'last_name': 'Kelly',
                'phone_number': '+353 87 456 7890',
            },
            {
                'email': 'liam.murphy@example.com',
                'password': 'Demo1234!',
                'first_name': 'Liam',
                'last_name': 'Murphy',
                'phone_number': '+353 86 567 8901',
            },
            {
                'email': 'aoife.ryan@example.com',
                'password': 'Demo1234!',
                'first_name': 'Aoife',
                'last_name': 'Ryan',
                'phone_number': '+353 85 678 9012',
            },
            {
                'email': 'conor.doyle@example.com',
                'password': 'Demo1234!',
                'first_name': 'Conor',
                'last_name': 'Doyle',
                'phone_number': '+353 87 789 0123',
            },
        ]

        members = []
        for data in members_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults=data,
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(f'  Created member: {user.get_full_name()}')
            else:
                self.stdout.write(f'  Member already exists: {user.get_full_name()}')
            members.append(user)

        olivia, liam, aoife, conor = members

        # --- Pilates Classes ---
        today = timezone.now().date()

        classes_data = [
            # This week
            {
                'title': 'Morning Flow Pilates',
                'description': 'A gentle, energising morning session focusing on breath work, spinal alignment, and full-body stretching. Perfect for all levels.',
                'instructor': sarah,
                'date': today + timedelta(days=1),
                'start_time': time(7, 30),
                'end_time': time(8, 30),
                'max_capacity': 12,
                'location': 'Studio A',
            },
            {
                'title': 'Core Strength & Stability',
                'description': 'An intermediate class targeting deep core muscles with challenging mat exercises. Build a strong centre and improve posture.',
                'instructor': james,
                'date': today + timedelta(days=1),
                'start_time': time(10, 0),
                'end_time': time(11, 0),
                'max_capacity': 10,
                'location': 'Studio B',
            },
            {
                'title': 'Reformer Basics',
                'description': 'Introduction to Reformer Pilates. Learn the fundamentals of the Reformer machine in a small group setting. No experience needed.',
                'instructor': emma,
                'date': today + timedelta(days=1),
                'start_time': time(12, 0),
                'end_time': time(13, 0),
                'max_capacity': 6,
                'location': 'Reformer Studio',
            },
            {
                'title': 'Power Pilates',
                'description': 'A high-intensity Pilates class combining traditional exercises with dynamic movements. For experienced practitioners looking for a challenge.',
                'instructor': james,
                'date': today + timedelta(days=2),
                'start_time': time(9, 0),
                'end_time': time(10, 0),
                'max_capacity': 10,
                'location': 'Studio A',
            },
            {
                'title': 'Prenatal Pilates',
                'description': 'Specially designed for expecting mothers. Gentle exercises to maintain strength, flexibility, and comfort throughout pregnancy.',
                'instructor': sarah,
                'date': today + timedelta(days=2),
                'start_time': time(11, 0),
                'end_time': time(12, 0),
                'max_capacity': 8,
                'location': 'Studio B',
            },
            {
                'title': 'Pilates for Runners',
                'description': 'Targeted session addressing common runner imbalances. Focus on hip stability, hamstring flexibility, and injury prevention.',
                'instructor': emma,
                'date': today + timedelta(days=3),
                'start_time': time(7, 0),
                'end_time': time(8, 0),
                'max_capacity': 12,
                'location': 'Studio A',
            },
            {
                'title': 'Lunchtime Express',
                'description': 'A focused 45-minute session perfect for your lunch break. Full-body workout with emphasis on efficiency.',
                'instructor': james,
                'date': today + timedelta(days=3),
                'start_time': time(12, 30),
                'end_time': time(13, 15),
                'max_capacity': 14,
                'location': 'Studio A',
            },
            {
                'title': 'Evening Restore & Stretch',
                'description': 'Wind down with gentle stretching, foam rolling, and restorative Pilates. Ideal for stress relief and recovery.',
                'instructor': sarah,
                'date': today + timedelta(days=3),
                'start_time': time(18, 30),
                'end_time': time(19, 30),
                'max_capacity': 12,
                'location': 'Studio B',
            },
            {
                'title': 'Advanced Reformer',
                'description': 'Challenging Reformer session for experienced clients. Complex sequences, spring variations, and advanced transitions.',
                'instructor': emma,
                'date': today + timedelta(days=4),
                'start_time': time(9, 0),
                'end_time': time(10, 0),
                'max_capacity': 6,
                'location': 'Reformer Studio',
            },
            {
                'title': 'Barre Pilates Fusion',
                'description': 'A dynamic blend of ballet barre work and Pilates principles. Sculpt and tone with small, precise movements.',
                'instructor': sarah,
                'date': today + timedelta(days=4),
                'start_time': time(17, 0),
                'end_time': time(18, 0),
                'max_capacity': 10,
                'location': 'Studio A',
            },
            # Next week
            {
                'title': 'Saturday Morning Flow',
                'description': 'Start your weekend right with a revitalising full-body Pilates session. All levels welcome.',
                'instructor': emma,
                'date': today + timedelta(days=6),
                'start_time': time(9, 30),
                'end_time': time(10, 30),
                'max_capacity': 14,
                'location': 'Studio A',
            },
            {
                'title': 'Mat Pilates Fundamentals',
                'description': 'Master the essential Pilates mat exercises with proper form and technique. Ideal for beginners or those returning to practice.',
                'instructor': james,
                'date': today + timedelta(days=7),
                'start_time': time(10, 0),
                'end_time': time(11, 0),
                'max_capacity': 12,
                'location': 'Studio B',
            },
        ]

        pilates_classes = []
        for data in classes_data:
            pc, created = PilatesClass.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                start_time=data['start_time'],
                defaults=data,
            )
            if created:
                self.stdout.write(f'  Created class: {pc.title} ({pc.date})')
            else:
                self.stdout.write(f'  Class already exists: {pc.title} ({pc.date})')
            pilates_classes.append(pc)

        # --- Bookings ---
        bookings_data = [
            # Morning Flow - popular class
            (olivia, pilates_classes[0], 'Looking forward to it!'),
            (liam, pilates_classes[0], ''),
            (aoife, pilates_classes[0], 'First class, a bit nervous!'),
            (conor, pilates_classes[0], ''),
            # Core Strength
            (olivia, pilates_classes[1], ''),
            (conor, pilates_classes[1], 'Need to work on my core'),
            # Reformer Basics
            (aoife, pilates_classes[2], 'Never tried Reformer before'),
            (liam, pilates_classes[2], ''),
            # Power Pilates
            (olivia, pilates_classes[3], ''),
            (liam, pilates_classes[3], 'Ready for a challenge'),
            (conor, pilates_classes[3], ''),
            # Lunchtime Express
            (aoife, pilates_classes[6], 'Perfect for my lunch break'),
            (olivia, pilates_classes[6], ''),
            # Evening Restore
            (liam, pilates_classes[7], 'Need this after leg day'),
            (aoife, pilates_classes[7], ''),
            (conor, pilates_classes[7], ''),
            # Barre Fusion
            (olivia, pilates_classes[9], ''),
            (aoife, pilates_classes[9], 'Love barre work!'),
            # Saturday Morning
            (olivia, pilates_classes[10], ''),
            (liam, pilates_classes[10], ''),
            (conor, pilates_classes[10], 'Weekend workout'),
        ]

        for user, pc, notes in bookings_data:
            booking, created = Booking.objects.get_or_create(
                user=user,
                pilates_class=pc,
                defaults={
                    'status': 'confirmed',
                    'notes': notes,
                },
            )
            if created:
                self.stdout.write(f'  Booked: {user.first_name} -> {pc.title}')
            else:
                self.stdout.write(f'  Booking exists: {user.first_name} -> {pc.title}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {len(instructors)} instructors, '
            f'{len(members)} members, {len(pilates_classes)} classes, '
            f'and {len(bookings_data)} bookings.'
        ))
        self.stdout.write(self.style.WARNING(
            '\nDemo login credentials (all accounts): password = Demo1234!'
        ))
