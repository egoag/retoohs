import datetime
from random import choice
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core import validators
from django.dispatch import receiver
from django.shortcuts import resolve_url
# from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from ss.utils import random_long_string, random_short_string

PLAN_CHOICES = (
    ('free', 'Free'),
)
METHOD_CHOICES = (
    ('aes-256-cfb', 'aes-256-cfb'),
    ('rc4-md5', 'rc4-md5'),
    ('salsa20', 'salsa20'),
    ('chacha20', 'chacha20'),
)
STATUS_CHOICES = (
    ('ok', '好用'),
    ('slow', '不好用'),
    ('fail', '坏了'),
)


# Create your models here.
class SSUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ss_user',
    )
    plan = models.CharField(
            '套餐',
            max_length=32,
            default='free',
            choices=PLAN_CHOICES,
    )
    last_check_in_time = models.DateTimeField(
            '最后签到时间',
            null=True,
            default=datetime.datetime.fromtimestamp(0),
            editable=False,
    )
    invite_code = models.OneToOneField(
            'InviteCode',
            on_delete=models.SET_NULL,
            related_name='used_by',
            null=True,
    )
    # ShadowSocks fields
    password = models.CharField(
            'ShadowSocks密码',
            max_length=32,
            validators=[validators.MinLengthValidator(6), ],
            default=random_short_string,
            db_column='passwd',
    )
    port = models.IntegerField(
            '端口',
            db_column='port',
            unique=True,
    )
    last_use_time = models.IntegerField(
            '最后使用时间',
            default=0,
            editable=False,
            help_text='时间戳',
            db_column='t',
    )
    upload_traffic = models.BigIntegerField(
            '上传流量',
            default=0,
            db_column='u',
    )
    download_traffic = models.BigIntegerField(
            '下载流量',
            default=0,
            db_column='d',
    )
    transfer_enable = models.BigIntegerField(
            '总流量',
            default=settings.DEFAULT_TRAFFIC,
            db_column='transfer_enable',
    )
    switch = models.BooleanField(
            'switch',
            default=True,
            db_column='switch'
    )
    enable = models.BooleanField(
            '开启',
            default=True,
            db_column='enable'
    )

    def __str__(self):
        return self.user.username

    def get_last_use_time(self):
        return timezone.datetime.fromtimestamp(self.last_use_time)

    def get_traffic(self):
        return '{:.2f}'.format((self.download_traffic + self.upload_traffic) / 1024 / 1024)

    def get_transfer(self):
        return '{:.2f}'.format(self.transfer_enable / 1024 / 1024 / 1024)

    def get_unused_traffic(self):
        return '{:.2f}'.format((self.transfer_enable - self.download_traffic - self.upload_traffic) / 1024 / 1024 / 1024)

    def get_used_percentage(self):
        return (self.download_traffic + self.upload_traffic) / self.transfer_enable * 100

    def can_check_in(self):
        return timezone.now() - datetime.timedelta(days=1) > self.last_check_in_time

    @classmethod
    def get_absolute_url(cls):
        return resolve_url('ss:index')

    def clean(self):
        # limit: 1024 < port < 50000
        if self.port:
            if not 1024 < self.port < 5000:
                raise ValidationError('端口必须大于1024,小于50000')
        else:
            max_port_user = SSUser.objects.order_by('-port').first()
            if max_port_user:
                self.port = max_port_user.port + choice([2, 3])
            else:
                self.port = settings.START_PORT

    class Meta:
        verbose_name = 'SS帐户'
        ordering = ('-last_check_in_time',)
        db_table = 'user'


class InviteCode(models.Model):
    code = models.CharField(
            '邀请码',
            primary_key=True,
            blank=True,
            max_length=40,
            default=random_long_string,
            # validators=[validators.MinLengthValidator(64), ],
    )
    user = models.ForeignKey(
            'SSUser',
            on_delete=models.CASCADE,
            related_name='invite_codes',
            null=True,
            blank=True,
            help_text='不选择用户生成的验证码将公开',
    )
    time_created = models.DateTimeField(
            '创建时间',
            editable=False,
            auto_now_add=True,
    )

    def clean(self):
        # generate code if code exists
        code_length = len(self.code or '')
        if 0 < code_length < 16:
            self.code = '{}{}'.format(
                    self.code,
                    random_long_string()
            )
        else:
            self.code = None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.clean()
        return super(InviteCode, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = '邀请码'
        ordering = ('-time_created',)


class Node(models.Model):
    name = models.CharField(
            '名字',
            max_length=32,
    )
    plan = models.CharField(
            '类型',
            max_length=32,
            default='free',
            choices=PLAN_CHOICES,
    )
    server = models.CharField(
            '服务器',
            max_length=128,
    )
    method = models.CharField(
            '加密类型',
            max_length=32,
            default='aes-256-cfb',
            choices=METHOD_CHOICES,
    )
    info = models.CharField(
            '简介',
            max_length=1024,
            blank=True,
            null=True,
    )
    status = models.CharField(
            '状态',
            max_length=32,
            default='ok',
            choices=STATUS_CHOICES,
    )
    weight = models.IntegerField(
            '排序',
            default=1,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-weight',)
        verbose_name = '节点'


@receiver(post_save, sender=SSUser)
def remove_invite_code_after_use(instance, created, **kwargs):
    if created:
        if instance.invite_code:
            instance.invite_code.delete()
