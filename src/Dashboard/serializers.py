from rest_framework import serializers
from products.models import Product
from orders.models import OrderProductDetail

class PopularProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProductDetail
        fields = '__all__'
        depth = 1

class FreshArrivalsProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        depth = 1

