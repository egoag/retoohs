from django.core.management.base import BaseCommand
from ss.models import SSUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        SSUser.objects.update(upload_traffic=0, download_traffic=0)
        print('Reset traffic success.')
