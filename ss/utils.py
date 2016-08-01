from django.utils.crypto import get_random_string


def random_long_string():
    return get_random_string(24)


def random_short_string():
    return get_random_string(6)
