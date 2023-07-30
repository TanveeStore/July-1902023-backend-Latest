from django.contrib import admin
from .models import DeliveryExecutive, DeliveryExeAddress, DeliveryExeBankAccount
from orders.models import DeliveryExeLiveData
# Register your models here.

class DeliveryExecutiveAdmin(admin.ModelAdmin):
    list_display=["user","driving_license","status"]
    #inlines = [VendorProfileAdmin]


admin.site.register(DeliveryExecutive, DeliveryExecutiveAdmin)


class DeliveryExeAddressAdmin(admin.ModelAdmin):
    list_display=["delivery_exe","address","locality","city","state","postcode","map_lat","map_lng"]
    #inlines = [VendorProfileAdmin]

admin.site.register(DeliveryExeAddress, DeliveryExeAddressAdmin)

class DeliveryExeBankAccountAdmin(admin.ModelAdmin):
    list_display=["delivery_exe","acc_bank_name", "acc_branch_name", "acc_ifsc", "acc_no", "is_default"]
    #inlines = [VendorProfileAdmin]

admin.site.register(DeliveryExeBankAccount, DeliveryExeBankAccountAdmin)


class DeliveryExeLiveDataAdmin(admin.ModelAdmin):
    list_display=["delivery_exe","live_map_lat", "live_map_lng", "live_oder", "live_status"]
    #inlines = [VendorProfileAdmin]

admin.site.register(DeliveryExeLiveData, DeliveryExeLiveDataAdmin)