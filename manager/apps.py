"""Apps config."""

from django.apps import AppConfig


class ManagerConfig(AppConfig):
    """Setup config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'manager'
