from django.db import models
from common.models import TimeStampMixin, User
# Create your models here.
# Coupon Model


class Offer(TimeStampMixin):
    offer_code = models.CharField(
        'Offer Code', unique=True, max_length=50, blank=False, null=False)
    valid_from = models.DateTimeField("Valid From", blank=False, null=False)
    valid_upto = models.DateTimeField("Valid Upto", blank=False, null=False)
    discount = models.DecimalField(
        "Discount (%)", max_digits=12, decimal_places=2, blank=False, null=False)
    max_discount_amt = models.DecimalField(
        "Max Discount Amount", max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    min_order_amt = models.DecimalField(
        "Min Order Amount",  blank=True, max_digits=12, decimal_places=2, null=True, default=0.00)
    is_one_time_use = models.BooleanField(
        "One Time Use", blank=True, null=True, default=False)
    is_new_customer = models.BooleanField(
        "New Customer", blank=True, null=True, default=False)
    offer_banner = models.ImageField(
        "Offer Banner", upload_to='offer_banner', blank=False, null=False)
    offer_short_desc = models.CharField(
        "Offer Short Desc", max_length=255, blank=False, null=False)
    offer_full_desc = models.TextField(
        "Offer Full Desc", blank=True, null=True)
    offer_status = models.CharField("Offer Status", max_length=50,
                                    choices=(
                                        ("active", "Active"),
                                        ("inactive", "Inactive"),),
                                    blank=False, null=False)

    def __str__(self):
        return str(self.offer_code) + " - " + str(self.discount) + "%"

    class Meta:
        verbose_name_plural = "Offers"
