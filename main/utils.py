import random


def is_email(string):
    from django.core.exceptions import ValidationError
    from django.core.validators import EmailValidator

    validator = EmailValidator()
    try:
        validator(string)
    except ValidationError:
        return False

    return True


def random_str(length, allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                     'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join([random.choice(allowed_chars) for _ in range(length)])


def random_str_20():
    return random_str(20)
