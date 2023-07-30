from rest_framework import serializers
from .models import Offer


# Serializer for Offer Model
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"
        # exclude = ["created_at", "updated_at"]

class OfferSerializerInPutValidatation(serializers.Serializer):
    offer_code = serializers.CharField(min_length=3, max_length=20, required=True)

    