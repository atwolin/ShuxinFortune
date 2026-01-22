from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Custom user model for future extensibility."""

    pass
