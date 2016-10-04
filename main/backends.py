from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from main.utils import is_email


class MyUserBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        user_model = get_user_model()

        if is_email(username):
            username_field = 'email'
        else:
            username_field = 'username'

        try:
            user = user_model._default_manager.get(**{username_field: username})
            if user.check_password(password):
                return user
        except user_model.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            user_model().set_password(password)
