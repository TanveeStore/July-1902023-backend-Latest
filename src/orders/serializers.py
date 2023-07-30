from rest_framework import serializers
from products.models import Product
from orders.models import ContactAddress, OrderDetail, OrderProductDetail, VendorOrderDetails, ReturnProduct
from products.serializers import ProductSerializer
from common.serializer.user_serializers import CommonUserSerializer
from CartSystem.serializers import WishlistProductSerializer
from drf_writable_nested import WritableNestedModelSerializer
from CartSystem.serializers import AddToCartSerializer

class ContactAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactAddress
        fields = '__all__'

class OrderDetailSerializer(serializers.ModelSerializer):
    address = ContactAddressSerializer()
    class Meta:
        model = OrderDetail
        fields = '__all__'
        #exclude = ('created_at', 'updated_at')



class OrderProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProductDetail
        # fields = '__all__'
        exclude = ('created_at', 'updated_at')
        depth = 1

class OrderProductDetailSerializerD2(serializers.ModelSerializer):
    class Meta:
        model = OrderProductDetail
        exclude = ['created_at', 'updated_at','order']
        depth = 2


class VendorOrderDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorOrderDetails
        fields = '__all__'
        depth = 3


class VendorOrderDetailsSerializerD0(serializers.ModelSerializer):
    class Meta:
        model = VendorOrderDetails
        fields = "__all__"

class VendorOrderDetailsSerializerD1(serializers.ModelSerializer):
    class Meta:
        model = VendorOrderDetails
        fields = "__all__"
        depth = 1
class VendorOrderDetailsSerializerD2(serializers.ModelSerializer):
    class Meta:
        model = VendorOrderDetails
        fields = "__all__"
        depth = 2


# ReturnProductSerializer
class ReturnProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProduct
        fields = '__all__'


# Use for Return Product
class OrderDetailSerializers2(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = "__all__"
