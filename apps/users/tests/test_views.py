import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestAuthenticationViews:
    """Tests for authentication endpoints."""

    def test_register_user(self, api_client):
        """Test user registration."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'newuser@example.com'
        assert 'password' not in response.data

    def test_register_user_with_mismatched_passwords(self, api_client):
        """Test registration with mismatched passwords fails."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'strongpass123',
            'password_confirm': 'differentpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_login_user(self, api_client, user):
        """Test user login with JWT."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_with_wrong_password(self, api_client, user):
        """Test login with wrong password fails."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_profile(self, authenticated_client, user):
        """Test getting current user profile."""
        url = reverse('user-me')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_update_user_profile(self, authenticated_client):
        """Test updating user profile."""
        url = reverse('user-update-profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Updated'
        assert response.data['last_name'] == 'Name'

    def test_unauthenticated_access_denied(self, api_client):
        """Test that unauthenticated users cannot access protected endpoints."""
        url = reverse('user-me')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
