import datetime

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy


class App(models.Model):
    PLATFORMS = (
        ('I', 'iOS'),
        ('A', 'Android')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=32, unique=True)

    app_name = models.CharField(max_length=70, default='Untitled App')
    platform = models.CharField(max_length=1, choices=PLATFORMS, default='I')
    bundle_id = models.CharField(max_length=255, unique=True)

    fb_app_id = models.CharField(max_length=32)
    fb_client_token = models.CharField(max_length=64)
    # fb_access_token = models.CharField(max_length=64)

    created_at = models.DateTimeField()

    def get_absolute_url(self):
        return reverse_lazy('trackbook:detail', kwargs={'pk': self.pk})

    def purchase_set_reversed(self):
        return self.purchase_set.order_by('-pk')

    def get_clear_purchases_count(self):
        total = self.purchase_set.count()
        valid = self.purchase_set.filter(is_valid=1).count()
        # ratio = invalid/total
        return valid

    def get_fraud_purchases_count(self):
        total = self.purchase_set.count()
        invalid = self.purchase_set.filter(is_valid=0).count()
        # ratio = invalid/total
        return invalid


class Purchase(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    log_timestamp = models.IntegerField()
    transaction_date = models.CharField(max_length=32, null=True)
    transaction_id = models.CharField(max_length=64)
    advertiser_id = models.CharField(max_length=64, null=True)
    fb_user_id = models.CharField(max_length=64, null=True)

    bundle_short_version = models.CharField(max_length=255)
    product_id = models.CharField(max_length=255)
    sum = models.FloatField()  # value_to_sum
    currency = models.CharField(max_length=3)

    is_sandbox = models.SmallIntegerField(default=0)
    is_valid = models.SmallIntegerField(default=0)
    is_logged = models.SmallIntegerField(default=0)

    ext_info = models.TextField()  # extinfo
    request_body = models.TextField()  # body

    def as_json(self):
        return dict(
            app_id=self.app_id,
            log_timestamp=self.log_timestamp,
            transaction_id=self.transaction_id,
            advertiser_id=self.advertiser_id,
            fb_user_id=self.fb_user_id,
            bundle_short_version=self.bundle_short_version,
            product_id=self.product_id,
            sum=self.sum,
            currency=self.currency,
            is_sandbox=self.is_sandbox,
            is_valid=self.is_valid,
            is_logged=self.is_logged,
            ext_info=self.ext_info,
            request_body=self.request_body,
        )

    def get_created_at(self):
        return datetime.datetime.utcfromtimestamp(self.log_timestamp)
