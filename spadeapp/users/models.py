from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import EmailField
from django.utils.translation import gettext_lazy as _

from spadeapp.users.managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Spade.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe

    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        # If no users exist, the first user is automatically a superuser
        if settings.ACCOUNT_FIRST_USER_ADMIN and not User.objects.exists():
            self.is_superuser = True
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ("last_name", "first_name")


class UserFavorite(models.Model):
    """Per-user favorites for files and processes."""

    RESOURCE_CHOICES = [
        ("files", "Files"),
        ("processes", "Processes"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    resource = models.CharField(max_length=20, choices=RESOURCE_CHOICES)
    resource_id = models.IntegerField()
    label = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("user", "resource", "resource_id")
        ordering = ("-pk",)

    def __str__(self):
        return f"{self.user.email} → {self.resource}/{self.resource_id}"
