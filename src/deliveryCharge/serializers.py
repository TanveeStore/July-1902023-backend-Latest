from rest_framework import serializers
from deliveryCharge.models import DeliveryCharge


# Serializer for Offer Model
class DeliveryChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCharge
        fields = "__all__"
        