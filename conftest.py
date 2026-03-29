import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user_data():
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User',
        'phone_number': '+1234567890',
    }


@pytest.fixture
def user(db, user_data):
    """Create a test user."""
    return User.objects.create_user(**user_data)


@pytest.fixture
def instructor(db):
    """Create a test instructor user."""
    return User.objects.create_user(
        email='instructor@example.com',
        password='testpass123',
        first_name='Jane',
        last_name='Instructor',
        phone_number='+1234567891',
        is_instructor=True,
    )


@pytest.fixture
def api_client():
    """DRF API test client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client
