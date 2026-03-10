"""
WSGI config for coreflow_booking_api project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coreflow_booking_api.settings')

application = get_wsgi_application()
