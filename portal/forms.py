from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, password_validation


class SignupForm(UserCreationForm):
    """
    A form for user registration.

    Form handles password validation and hashing.
    """

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        # model based fields
        fields = (
            "username",
            "email",
        )
        help_texts = {
            f: "" for f in fields
        }
        labels = {
            "username": "Username",
            "email": "Email",
            "password1": "Password",
            "password2": "Confirm Password",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove dynamic form derived fields
        for name in ("password1", "password2"):
            self.fields[name].help_text = ""

        self.fields["email"].required = True

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        password_validation.validate_password(password, self.instance)
        return password

    @property
    def password_help_list(self):
        return password_validation.password_validators_help_texts()