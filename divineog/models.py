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

    created_at = models.DateTimeField()

    def get_absolute_url(self):
        return reverse_lazy('divineog:detail', kwargs={'pk': self.pk})


class Purchase(models.Model):

    app = models.ForeignKey(App, on_delete=models.CASCADE)

    transaction_id = models.CharField(max_length=64, unique=True)
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
    log_timestamp = models.IntegerField()  # logTime
