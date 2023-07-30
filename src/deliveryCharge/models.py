from django.db import models
from common.models import TimeStampMixin

# Create your models here.
class DeliveryCharge(TimeStampMixin):
    
    deliveryPrice = models.DecimalField(
        "Delivery Charge", max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    min_order_amt = models.DecimalField(
        "Min Order Amount",  blank=True, max_digits=12, decimal_places=2, null=True, default=0.00)
    max_order_amt = models.DecimalField(
        "Max Order Amount", max_digits=12, decimal_places=2, blank=True, null=True, default=0.00)
    short_desc = models.CharField(
        "Description", max_length=255, blank=True, null=True)
    
    status = models.CharField("Status", max_length=50,
                                    choices=(
                                        ("active", "Active"),
                                        ("inactive", "Inactive"),),
                                    blank=False, null=False)

    def __str__(self):
        return str(self.short_desc)

    class Meta:
        verbose_name_plural = "Delivery Charge"