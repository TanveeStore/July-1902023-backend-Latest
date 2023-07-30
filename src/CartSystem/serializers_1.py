from rest_framework import serializers
from products.serializers import ProductSerializer
from django.conf import settings

from CartSystem.models import WishList, AddToCart
from common.models import User
from common.serializer.user_serializers import UserSerializer
from products.models import Product


class WishlistProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'short_description', 'main_image']


class WishlistSerializer(serializers.ModelSerializer):
    product = WishlistProductSerializer()

    class Meta:
        fields = ['product']
        # fields = '__all__'
        model = WishList
        depth = 2


class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddToCart
        # fields = '__all__'
        exclude = ('created_at', 'updated_at')


class AddToWishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = AddToCart
        fields = ["user", "product", "quantity"]
