from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.models import AbstractUser

PLAN_CHOICES = (
    ('free', 'Free'),
)
METHOD_CHOICES = (
    ('aes-256-cfb', 'aes-256-cfb'),
)
STATUS_CHOICES = (
    ('ok', 'OK'),
)


# Create your models here.
class SSUser(models.Model):
    plan = models.CharField(
        '套餐',
        max_length=32,
        default='free',
        choices=PLAN_CHOICES,
    )
    last_check_in_time = models.DateTimeField(
        '最后签到时间',
        null=True,
        editable=False,
    )
    invite_code = models.CharField(
        '邀请码',
        editable=False,
        max_length=128,
    )
    # ShadowSocks fields
    ss_password = models.CharField(
        'ShadowSocks密码',
        max_length=32,
        default=get_random_string,
        db_column='passwd',
    )
    port = models.IntegerField(
        '端口',
        db_column='port',
    )
    last_use_time = models.IntegerField(
        '最后使用时间',
        default=0,
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

    def __str__(self):
        return self.username

    class Meta:
        ordering = ('-last_check_in_time',)


class InviteCode(models.Model):
    code = models.CharField(
        '邀请码',
        max_length=128,
    )
    time_created = models.DateTimeField(
        '创建时间',
        editable=False,
        auto_now_add=True,
    )


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
