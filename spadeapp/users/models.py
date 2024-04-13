from django.conf import settings
from django.contrib.auth.models import AbstractUser
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
