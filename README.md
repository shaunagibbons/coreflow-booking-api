# CoreFlow Booking API

A production-ready REST API and backend for an enterprise-style Pilates studio booking system, built with Django and Django REST Framework. It handles authentication, class scheduling, booking management, and integrates with external services for email notifications and media storage.

**Live API:** Deployed on [Render](https://render.com) with a PostgreSQL database.

---

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [Data Models & Relationships](#data-models--relationships)
4. [API Endpoints](#api-endpoints)
5. [Authentication](#authentication)
6. [Business Rules](#business-rules)
7. [Setup & Installation](#setup--installation)
8. [Environment Variables](#environment-variables)
9. [Running the Application](#running-the-application)
10. [Testing](#testing)
11. [Demo Data & Seed Command](#demo-data--seed-command)
12. [API Documentation (Swagger)](#api-documentation-swagger)
13. [Deployment](#deployment)
14. [External Integrations](#external-integrations)

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Framework | Django 5.1.3 | Web framework |
| API | Django REST Framework 3.15.2 | RESTful API layer |
| Database | PostgreSQL + psycopg2 | Relational data storage |
| Authentication | djangorestframework-simplejwt 5.3.1 | JWT token-based auth |
| API Docs | drf-yasg 1.21.7 | Swagger / OpenAPI schema |
| Email | django-sendgrid-v5 1.2.3 | Transactional email via SendGrid |
| Media Storage | django-cloudinary-storage 0.3.0 | Cloud image uploads via Cloudinary |
| Static Files | WhiteNoise 6.7.0 | Compressed static file serving |
| CORS | django-cors-headers 4.3.1 | Cross-origin request handling |
| Server | Gunicorn 22.0.0 | Production WSGI server |
| Testing | pytest 8.0.2 + pytest-django 4.8.0 | Automated test suite |

---

## Project Structure

```
coreflow-booking-api/
├── apps/
│   ├── users/                  # User management & authentication
│   │   ├── models.py           # Custom User model (email-based)
│   │   ├── views.py            # Registration, login, profile, password reset
│   │   ├── serializers.py      # User data validation & transformation
│   │   ├── urls.py             # Auth route definitions
│   │   ├── admin.py            # User admin configuration
│   │   └── tests/
│   │       ├── test_views.py   # Auth & profile endpoint tests
│   │       └── test_models.py  # User model validation tests
│   │
│   └── scheduling/             # Class scheduling & booking management
│       ├── models.py           # PilatesClass & Booking models
│       ├── views.py            # Class CRUD, booking workflows
│       ├── serializers.py      # Scheduling data validation
│       ├── urls.py             # Scheduling route definitions
│       ├── admin.py            # Class & booking admin configuration
│       ├── management/
│       │   └── commands/
│       │       └── seed_demo_data.py  # Demo data seeder
│       └── tests/
│           ├── test_models.py      # Model validation tests
│           ├── test_bookings.py    # Booking workflow tests
│           └── test_validation.py  # Business rule tests
│
├── coreflow_booking_api/       # Project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
│
├── conftest.py                 # Shared pytest fixtures
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
├── manage.py                   # Django CLI
├── Procfile                    # Process definition for deployment
├── build.sh                    # Build script for Render
├── render.yaml                 # Render deployment blueprint
└── .env.example                # Environment variable template
```

---

## Data Models & Relationships

```
User (1) ───────< PilatesClass (via instructor FK)
User (1) ───────< Booking (via user FK)
PilatesClass (1) ───────< Booking (via pilates_class FK)
```

### User

Custom user model with email-based authentication (no username field).

| Field | Type | Details |
|---|---|---|
| `email` | EmailField | **Primary login identifier**, unique |
| `first_name` | CharField | Required |
| `last_name` | CharField | Required |
| `phone_number` | CharField | Optional |
| `is_instructor` | BooleanField | Grants class creation permissions |
| `profile_image` | CloudinaryField | Optional profile picture |

### PilatesClass

Represents a scheduled Pilates class with capacity management.

| Field | Type | Details |
|---|---|---|
| `title` | CharField | Class name |
| `description` | TextField | Optional details |
| `instructor` | ForeignKey(User) | Must be an instructor |
| `date` | DateField | Class date |
| `start_time` | TimeField | Class start |
| `end_time` | TimeField | Must be after `start_time` |
| `max_capacity` | IntegerField | Default: 10 |
| `location` | CharField | Venue name |

**Computed properties:** `is_full`, `available_spots`, `can_book()`

### Booking

Links a user to a class with status tracking.

| Field | Type | Details |
|---|---|---|
| `user` | ForeignKey(User) | Student making the booking |
| `pilates_class` | ForeignKey(PilatesClass) | Class being booked |
| `status` | CharField | `pending`, `confirmed`, or `cancelled` |
| `notes` | TextField | Optional booking notes |

**Constraint:** Unique on `(user, pilates_class)` -- one booking per user per class.

---

## API Endpoints

### Authentication (`/api/auth/`)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register a new user | None |
| `POST` | `/api/auth/login/` | Obtain JWT access & refresh tokens | None |
| `POST` | `/api/auth/refresh/` | Refresh an expired access token | None |
| `GET` | `/api/auth/users/me/` | Get current user profile | Required |
| `PATCH` | `/api/auth/users/update_profile/` | Update profile (name, phone, image) | Required |
| `POST` | `/api/auth/users/change_password/` | Change password | Required |
| `GET` | `/api/auth/users/` | List all users (staff only) | Staff |
| `GET` | `/api/auth/users/{id}/` | Get user by ID | Required |
| `POST` | `/api/auth/password-reset/` | Request password reset email | None |
| `POST` | `/api/auth/password-reset-confirm/` | Confirm password reset with token | None |

### Classes (`/api/classes/`)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/classes/` | List classes (with filtering) | Required |
| `GET` | `/api/classes/{id}/` | Get class details | Required |
| `POST` | `/api/classes/` | Create a class | Instructor |
| `PATCH` | `/api/classes/{id}/` | Update a class | Instructor (owner) |
| `DELETE` | `/api/classes/{id}/` | Delete a class | Admin |
| `GET` | `/api/classes/{id}/bookings/` | View class bookings | Instructor (owner) |

**Query parameters for `GET /api/classes/`:**

| Parameter | Description | Example |
|---|---|---|
| `date_from` | Filter by start date | `?date_from=2026-04-01` |
| `date_to` | Filter by end date | `?date_to=2026-04-30` |
| `instructor` | Filter by instructor ID | `?instructor=3` |
| `location` | Case-insensitive partial match | `?location=studio` |
| `available_only` | Only bookable classes | `?available_only=true` |
| `search` | Full-text search (title, description, location, instructor name) | `?search=reformer` |

### Bookings (`/api/bookings/`)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/bookings/` | List current user's bookings | Required |
| `GET` | `/api/bookings/{id}/` | Get booking details | Required |
| `POST` | `/api/bookings/` | Create a new booking | Required |
| `GET` | `/api/bookings/upcoming/` | Get upcoming bookings | Required |
| `GET` | `/api/bookings/past/` | Get past bookings | Required |
| `POST` | `/api/bookings/{id}/cancel/` | Cancel a booking | Required |

### Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/docs/` | Swagger UI interactive documentation |
| `GET` | `/api/redoc/` | ReDoc API documentation |
| `GET` | `/admin/` | Django admin interface |

---

## Authentication

The API uses **JWT (JSON Web Tokens)** for stateless authentication.

### Login Flow

```
1. POST /api/auth/login/  { "email": "...", "password": "..." }
   → Returns { "access": "<token>", "refresh": "<token>" }

2. Include the access token in subsequent requests:
   Authorization: Bearer <access_token>

3. When the access token expires, refresh it:
   POST /api/auth/refresh/  { "refresh": "<refresh_token>" }
   → Returns a new { "access": "<token>" }
```

### Token Configuration

| Setting | Default | Env Variable |
|---|---|---|
| Access token lifetime | 60 minutes | `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` |
| Refresh token lifetime | 7 days | `JWT_REFRESH_TOKEN_LIFETIME_DAYS` |
| Token rotation | Enabled | -- |
| Blacklist after rotation | Enabled | -- |

### Password Reset Flow

```
1. POST /api/auth/password-reset/  { "email": "user@example.com" }
   → Sends email with reset link containing uid and token

2. POST /api/auth/password-reset-confirm/
   { "uid": "...", "token": "...", "new_password": "...", "confirm_password": "..." }
   → Password is reset
```

---

## Business Rules

| Rule | Description |
|---|---|
| **Double-booking prevention** | A user cannot book the same class twice (database unique constraint) |
| **Capacity enforcement** | Bookings are rejected when a class reaches `max_capacity` |
| **Booking cutoff time** | Bookings must be made at least 2 hours before class start |
| **Cancellation window** | Cancellations must be made at least 2 hours before class start |
| **Instructor-only class creation** | Only users with `is_instructor=True` can create or edit classes |
| **Instructor isolation** | Instructors can only manage their own classes |
| **User booking isolation** | Users can only view and manage their own bookings (staff can view all) |
| **Email uniqueness** | Email addresses are unique across all user accounts |

---

## Setup & Installation

### Prerequisites

- **Python 3.11+**
- **PostgreSQL** (running locally or a connection URL)
- **pip** (Python package manager)

### Step-by-Step Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/<your-username>/coreflow-booking-api.git
   cd coreflow-booking-api
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # macOS / Linux
   # .venv\Scripts\activate         # Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create the PostgreSQL database:**

   ```bash
   psql -U postgres
   ```

   ```sql
   CREATE DATABASE coreflow_booking;
   \q
   ```

5. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in your local values (see [Environment Variables](#environment-variables) below).

6. **Run database migrations:**

   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (admin account):**

   ```bash
   python manage.py createsuperuser
   ```

8. **(Optional) Seed demo data:**

   ```bash
   python manage.py seed_demo_data
   ```

9. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

   The API is now available at `http://localhost:8000/`.

---

## Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (Option A: individual fields)
DB_NAME=coreflow_booking
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Database Settings (Option B: connection URL -- overrides Option A)
DATABASE_URL=

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# SendGrid Email
SENDGRID_API_KEY=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@coreflow.com

# Frontend URL (used in password reset emails)
FRONTEND_URL=http://localhost:5173

# Cloudinary Media Storage
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

> **Note:** `SENDGRID_API_KEY` and `CLOUDINARY_*` variables are only required if you need email sending and image upload functionality. The core API will run without them.

---

## Running the Application

### Development Server

```bash
python manage.py runserver
```

Access at: `http://localhost:8000/`

### Production Server (Gunicorn)

```bash
gunicorn coreflow_booking_api.wsgi --log-file -
```

### Applying Migrations

```bash
python manage.py makemigrations    # Generate migration files after model changes
python manage.py migrate           # Apply migrations to the database
```

### Collecting Static Files

```bash
python manage.py collectstatic --noinput
```

---

## Testing

The project uses **pytest** with **pytest-django** for automated testing. The test suite contains **36 tests** across 5 test modules covering models, views, business logic, and permissions.

### Running Tests

```bash
# Run all tests
pytest

# Verbose output with test names
pytest -v

# Run tests for a specific app
pytest apps/users/
pytest apps/scheduling/

# Run a specific test file
pytest apps/scheduling/tests/test_bookings.py

# Run a specific test by name
pytest -k "test_booking_creation"

# Run tests excluding those marked as slow
pytest -m "not slow"

# Run with coverage report (requires pytest-cov)
pip install pytest-cov
pytest --cov=apps --cov-report=term-missing
```

### Test Coverage Areas

| Module | Tests | Coverage |
|---|---|---|
| `users/tests/test_views.py` | 10 | Registration, login, JWT refresh, profile view/update, password change, password reset flow |
| `users/tests/test_models.py` | 2 | User creation, instructor creation, email uniqueness |
| `scheduling/tests/test_models.py` | 5 | PilatesClass creation/validation, Booking creation/constraints |
| `scheduling/tests/test_bookings.py` | 14 | Booking CRUD, capacity enforcement, cutoff time, cancellation, filtering, admin access |
| `scheduling/tests/test_validation.py` | 5 | Double-booking prevention, class validation, permission checks |

### Test Fixtures

Shared fixtures are defined in `conftest.py`:

| Fixture | Description |
|---|---|
| `user_data` | Dictionary of sample user registration data |
| `user` | Pre-created non-instructor user |
| `instructor` | Pre-created instructor user |
| `api_client` | Unauthenticated DRF `APIClient` |
| `authenticated_client` | `APIClient` with JWT authentication for `user` |

### Key Test Scenarios

- **User registration** with password validation (length, complexity)
- **JWT login and token refresh** cycle
- **Profile management** (view, update, change password)
- **Password reset** request and confirmation with token
- **Class creation** by instructors with time/capacity validation
- **Booking creation** with capacity and cutoff time enforcement
- **Double-booking prevention** (unique constraint)
- **Booking cancellation** within the allowed time window
- **Upcoming/past booking** filtering
- **Permission enforcement** (instructor-only, user-isolation, staff-only)

---

## Demo Data & Seed Command

The `seed_demo_data` management command populates the database with realistic sample data for development and demonstration purposes.

```bash
python manage.py seed_demo_data
```

### What Gets Created

**3 Instructors:**

| Name | Email | Password |
|---|---|---|
| Sarah Mitchell | sarah.mitchell@coreflow.com | `Demo1234!` |
| James Brennan | james.brennan@coreflow.com | `Demo1234!` |
| Emma Walsh | emma.walsh@coreflow.com | `Demo1234!` |

**4 Members:**

| Name | Email | Password |
|---|---|---|
| Olivia Kelly | olivia.kelly@example.com | `Demo1234!` |
| Liam Murphy | liam.murphy@example.com | `Demo1234!` |
| Aoife Ryan | aoife.ryan@example.com | `Demo1234!` |
| Conor Doyle | conor.doyle@example.com | `Demo1234!` |

**12+ Pilates classes** scheduled across the next 2 weeks with various types (Morning Flow, Core Strength, Reformer, Power Pilates, Prenatal, Express, and more).

**20+ sample bookings** linking members to classes.

> The command is **idempotent** -- it is safe to run multiple times without creating duplicates.

---

## API Documentation (Swagger)

Interactive API documentation is auto-generated and available at:

- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`

To authenticate in the Swagger UI, click **Authorize** and enter:

```
Bearer <your_access_token>
```

---

## Deployment

The application is configured for deployment on **Render** using the included `render.yaml` blueprint.

### Render Blueprint

The `render.yaml` file defines:

- A **web service** running Python 3.11.6 with Gunicorn
- A **PostgreSQL database** (free tier)
- Automatic build steps: install dependencies, collect static files, run migrations, seed demo data

### Build Process

The `build.sh` script runs during deployment:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_demo_data
```

### Production Security

When `DEBUG=False`, the following security settings are automatically enabled:

- HTTPS/SSL redirect
- Secure session and CSRF cookies
- HSTS headers (1 year, with subdomains and preload)
- XSS protection headers
- Content-Type sniffing protection

---

## External Integrations

### SendGrid (Email)

Used for transactional emails including:

- **Password reset emails** with secure tokenised links
- **Booking confirmation emails**

Requires the `SENDGRID_API_KEY` environment variable to be set.

### Cloudinary (Media Storage)

Used for storing user-uploaded files such as profile images. Media files are served directly from Cloudinary's CDN rather than the application server.

Requires `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` environment variables.

---

## AI Usage Acknowledgement

This module is classified as Yellow under institutional AI guidance. AI tools were utilised for drafting docstrings, generating initial test cases, and debugging complex Django ORM queries. All generated code was manually reviewed, refined, and tested to ensure a complete understanding of the underlying architecture.
