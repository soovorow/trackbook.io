from django.core.management.base import BaseCommand
from django.utils import timezone

from trackbook.models import Purchase


class Command(BaseCommand):
    help = 'Horn daily report'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')
        p = Purchase.objects.filter(transaction_date__date=timezone.now())
        self.stdout.write(p.count())
        self.stdout.write("Done;" % time)