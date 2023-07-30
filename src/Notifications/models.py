from django.db import models
from common.models import User, TimeStampMixin

# Notification Model
class Notifications(TimeStampMixin):
    notificationTypeChoice = (
        ("alert", "Alert"),
        ("delivery", "Delivery"),
        ("offer", "Offer"),
        ("order", "Order"),
        ("product", "Product"),
        ("transaction", "Transaction"),
        ("other", "Other"),
    )

    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    notificationText = models.TextField(blank=False, null=False)
    notificationType = models.CharField(choices=notificationTypeChoice, max_length=150, blank=False, null=False, default = "other")
    seenStatus = models.BooleanField(default=False)


    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return str(self.user)
