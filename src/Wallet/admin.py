from django.contrib import admin
from Wallet.models import MyWallet

# Register Mywallet Model.
class MyWalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','transactionId', 'walletBalance', 'trasactionAmt', 'transactionType', 'status', 'orderNumber', 'created_at']
    list_display_links = ['id', 'user']
    search_fields = ['user__first_name', 'user__last_name']
admin.site.register(MyWallet, MyWalletAdmin)
