from django.contrib import admin
from .models import Vendor, User, VendorBankAccount, VendorAddress
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

# class VendorProfileAdmin(admin.StackedInline):
#     model = Vendor
#     can_delete=False
#     verbose_name_plural="Vendor Profile"
#     one_to_one = "user"

class VendorAdmin(admin.ModelAdmin):
    list_display=["user","org_name"]
    #inlines = [VendorProfileAdmin]


admin.site.register(Vendor, VendorAdmin)

class VendorAddressAdmin(admin.ModelAdmin):
    list_display=["vendor","address","locality","city","state","postcode"]
    search_fields = ["vendor__user__first_name", "vendor__user__last_name", "name", "address"]
admin.site.register(VendorAddress, VendorAddressAdmin)

class VendorBankAccountAdmin(admin.ModelAdmin):
    list_display=["vendor","acc_bank_name", "acc_branch_name", "acc_ifsc", "acc_no", "is_default"]

admin.site.register(VendorBankAccount, VendorBankAccountAdmin)