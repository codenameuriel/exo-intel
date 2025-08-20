from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    """
    A form for user registration.

    Form handles password validation and hashing.
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
        )
