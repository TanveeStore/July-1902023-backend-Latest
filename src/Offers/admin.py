from django.contrib import admin
from Offers.models import Offer

# Register your models here.
class OfferAdmin(admin.ModelAdmin):
    list_display = ['id', 'offer_code', 'valid_from','valid_upto', 'discount']
    list_display_links = ['id','offer_code']

admin.site.register(Offer, OfferAdmin)