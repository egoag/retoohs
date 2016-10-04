from django.db import models
from hashlib import md5
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    balance = models.DecimalField(
        '余额',
        decimal_places=2,
        max_digits=10,
        default=0,
        editable=False,
        null=True,
        blank=True,
    )

    def set_password(self, raw_password):
        self.password = md5(raw_password.encode()).hexdigest()
        self._password = raw_password

    class Meta(AbstractUser.Meta):
        verbose_name = '用户'
