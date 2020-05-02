import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from trackbook.logger import Logger
from trackbook.models import Purchase
from trackbook.utils.currencyconverter import CurrencyConverter


class Command(BaseCommand):
    help = 'Horn daily report'

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        p = Purchase.objects.filter( transaction_date__contains=yesterday)
        count = p.count()

        horn = f"Daily Report \n" \
               f"Date: {yesterday} UTC \n"

        if count > 0:
            total = 0
            for purch in p:
                total += CurrencyConverter(purch.currency, purch.sum).to_usd()
            horn += "Total purchases: %s \n" % count
            horn += "Estimated revenue ~$%1.2f" % total
        else:
            horn += "There was no any transactions. Sad, but true."

        Logger.horn(horn)
        self.stdout.write(f"{horn}")
        self.stdout.write("Report Sent.")
