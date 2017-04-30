import datetime
from hashlib import md5
from django.db import models
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from main.utils import random_str_20


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
    email_verified = models.BooleanField(
        'Email Verified',
        default=False,
    )

    def set_password(self, raw_password):
        self.password = md5(raw_password.encode()).hexdigest()
        self._password = raw_password

    def check_password(self, raw_password):
        return self.password == md5(raw_password.encode()).hexdigest()

    def get_age(self):
        now = datetime.datetime.now()
        date_joined = self.date_joined
        age = ''
        if now.year - date_joined.year != 0:
            age += '{}年'.format(now.year - date_joined.year)
        if now.month - date_joined.month != 0:
            age += '{}月'.format(now.month - date_joined.month)

        age += '{}天'.format(now.day - date_joined.day)
        return age

    class Meta(AbstractUser.Meta):
        verbose_name = '用户'


class EmailVerification(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='email_verifications',
        null=True,
        blank=True,
    )
    code = models.CharField(
        'Verification Code',
        max_length=20,
        default=random_str_20,
    )
    time_created = models.DateTimeField(
        'Created at',
        auto_now_add=True,
        editable=False,
    )


@receiver(post_save, sender=User)
def email_verify(sender, instance, created=False, *args, **kwargs):
    if created:
        email_verification = EmailVerification.objects.create(user=instance)
        message = render_to_string('main/email_verification_email.html', context={
            'site_name': 'retoohs',
            'username': instance.username,
            'active_link': settings.EMAIL_VERIFICATION_URL.format(email_verification.code),
        })
        send_mail(
            'Active your account',
            message,
            settings.EMAIL_SENDER,
            [instance.email],
        )


User._meta.get_field('username').max_length = 64
User._meta.get_field('email')._unique = True
User._meta.get_field('email').help_text = '激活账号，找回密码需要。'
