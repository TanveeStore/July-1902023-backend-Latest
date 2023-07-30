from rest_framework import serializers
from Wallet.models import MyWallet



# Write a Serialzer for MyWallet Model
class MyWalletSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MyWallet
        fields = "__all__"
        # fields = ['id', 'user', 'amount', "created_at", "updated_at"]


