# Coreflow Booking API - Setup Instructions

## Prerequisites
- Python 3.10+
- PostgreSQL 12+
- pip

## Setup Steps

### 1. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env and update with your database credentials and secret key
```

### 4. Create PostgreSQL database
```bash
createdb coreflow_booking
# Or using psql:
# psql -U postgres
# CREATE DATABASE coreflow_booking;
```

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```

The API will be available at: http://localhost:8000

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest apps/users/tests/test_models.py

# Run with verbose output
pytest -v
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/users/me/` - Get current user profile
- `PATCH /api/auth/users/update_profile/` - Update profile
- `POST /api/auth/users/change_password/` - Change password

### Classes
- `GET /api/classes/` - List all classes (supports filtering)
- `GET /api/classes/{id}/` - Get class details
- `POST /api/classes/` - Create class (instructor only)
- `PATCH /api/classes/{id}/` - Update class (instructor only)
- `DELETE /api/classes/{id}/` - Delete class (admin only)

### Bookings
- `GET /api/bookings/` - List user's bookings
- `GET /api/bookings/upcoming/` - Get upcoming bookings
- `GET /api/bookings/past/` - Get past bookings
- `POST /api/bookings/` - Create booking
- `POST /api/bookings/{id}/cancel/` - Cancel booking

## Query Parameters for Classes

- `date_from` - Filter by start date (YYYY-MM-DD)
- `date_to` - Filter by end date (YYYY-MM-DD)
- `instructor` - Filter by instructor ID
- `location` - Filter by location (partial match)
- `available_only=true` - Show only bookable classes
- `search` - Search in title, description, location

## Project Structure

```
coreflow-booking-api/
├── apps/
│   ├── users/              # User management app
│   │   ├── models.py       # Custom User model
│   │   ├── serializers.py  # User serializers
│   │   ├── views.py        # Auth views
│   │   ├── urls.py         # User routes
│   │   ├── admin.py        # Admin configuration
│   │   └── tests/          # User tests
│   └── scheduling/         # Scheduling app
│       ├── models.py       # PilatesClass & Booking models
│       ├── serializers.py  # Scheduling serializers
│       ├── views.py        # Class & booking views
│       ├── urls.py         # Scheduling routes
│       ├── admin.py        # Admin configuration
│       └── tests/          # Scheduling tests
├── coreflow_booking_api/
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
├── conftest.py             # Pytest fixtures
├── .env.example            # Environment variables template
└── .gitignore              # Git ignore rules
```

## Business Rules Implemented

1. **Double-booking prevention**: Users cannot book the same class twice
2. **Capacity enforcement**: Classes cannot exceed maximum capacity
3. **Cut-off time enforcement**: Bookings must be made at least 2 hours before class
4. **Cancellation rules**: Bookings can only be cancelled before the cut-off time
5. **Permission checks**: Only instructors can create/edit classes
6. **Unique email**: Email addresses must be unique across users

## Next Steps

After setting up the API, you can:
1. Use the admin panel to create test data
2. Test endpoints using Swagger UI
3. Set up the frontend client (coreflow-booking-client)
4. Configure production settings for deployment
