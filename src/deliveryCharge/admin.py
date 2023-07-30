from django.contrib import admin
from deliveryCharge.models import DeliveryCharge


# Register DeliveryCharge model here.
class DeliveryChargeAdmin(admin.ModelAdmin):
    list_display = ['id', 'deliveryPrice', 'min_order_amt', 'max_order_amt', 'short_desc', 'status', "created_at", "updated_at"]
    list_display_links = ['id']

admin.site.register(DeliveryCharge, DeliveryChargeAdmin)

