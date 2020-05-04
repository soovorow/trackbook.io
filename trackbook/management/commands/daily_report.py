import datetime

from django.core.management.base import BaseCommand

from trackbook.logger import Logger
from trackbook.models import Purchase
from trackbook.services.currencyconverter import CurrencyConverter


class Command(BaseCommand):
    help = 'Horn daily report'

    def handle(self, *args, **kwargs):
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        p = Purchase.objects.filter(is_logged=1, transaction_date__contains=yesterday)
        count = p.count()

        horn = f"📬💌🎉 *Report:* {yesterday} UTC \n"

        if count > 0:
            total = 0
            for purch in p:
                total += CurrencyConverter(purch.currency, purch.sum).to_usd()
            horn += "~$%1.2f " % total
            horn += "(%s) \n" % count
        else:
            horn += "There was no any transactions. Sad, but true."

        Logger.horn(horn)
        self.stdout.write(f"{horn}")
        self.stdout.write("Report Sent.")
