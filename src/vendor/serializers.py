# from attr import validate
from rest_framework import serializers
from vendor.models import Vendor, VendorBankAccount
from vendor.models import VendorAddress
from common.models import User
from phonenumber_field.modelfields import PhoneNumberField
from products.models import Product, Category, Size, UnitofMeasure, Brand, ProductImage

from products.serializers import (
    CategorySerializer,
    ProductSerializer,
    SizeSerializer,
    UoMSerializer,
    ProductImageSerializer,
    BrandSerializer
)
from orders.models import OrderProductDetail, OrderDetail

class VendorRegSerializer(serializers.Serializer):
    first_name= serializers.CharField(required=True,min_length=3)
    last_name= serializers.CharField(required=True,min_length=3)
    email = serializers.EmailField(required=True)
    mobile = PhoneNumberField(blank=False, null=False, unique=True)
    org_name = serializers.CharField(required=True,min_length=5)

    def validate_email(self, email):
        check_email = User.objects.filter(email=email).first()
        if check_email:
            raise serializers.ValidationError("Email already exists!")
        return email

    def validate_mobile(self, mobile):
        check_mobile = User.objects.filter(mobile=mobile).first()
        if check_mobile:
            raise serializers.ValidationError("Mobile No already exists!")
        return mobile



class VendorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True,min_length=6)
    
class VendorChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True,min_length=6)
    new_password = serializers.CharField(required=True,min_length=6)
    
class VendorProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password","is_superuser","is_staff","groups","user_permissions","role","last_login","created_at","updated_at","is_admin","is_new_user"]
    
class VendorProfileBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["org_name",
        "telephone_1",
        "telephone_2",
        "company_pancard",
        "company_pancard_doc",
        "adhar_udyam_udoyog",
        "adhar_udyam_udoyog_doc",
        "gst_number"]

class VendorProfileBusinessSerializerUpdate(serializers.ModelSerializer):
    org_name=serializers.CharField(max_length=50)
    telephone_1=PhoneNumberField(blank=False, null=False, unique=True)
    telephone_2=PhoneNumberField(blank=False, null=False, unique=True)
    company_pancard=serializers.CharField(required=True, max_length=50)
    company_pancard_doc=serializers.ImageField(required=False)
    adhar_udyam_udoyog=serializers.CharField(max_length=50)
    adhar_udyam_udoyog_doc=serializers.ImageField(required=False)
    gst_number=serializers.CharField(max_length=50)

    class Meta:
        model = Vendor
        fields = ["org_name",
        "telephone_1",
        "telephone_2",
        "company_pancard",
        "company_pancard_doc",
        "adhar_udyam_udoyog",
        "adhar_udyam_udoyog_doc",
        "gst_number"]

class VendorProfileBasicSerializerUpdate(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    gender = serializers.CharField(required=False)
    email = serializers.EmailField(required=True)
    alternate_email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=True)
    profile_pic = serializers.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'gender', 'email', 'alternate_email', 'mobile', 'profile_pic']


class VendorProfileStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ["status"]

    
class VendorProfileAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAddress
        fields = ["id","vendor","name","address","address","locality","city","state","postcode","map_lat","map_lng"]

class VendorProfileBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBankAccount
        fields = ["id","vendor","acc_bank_name","acc_branch_name","acc_branch_name","acc_ifsc","acc_no","is_default"]




class VendorProductPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

        # fields =["name", "short_description", "description", "status",
        #           "weight","category", "qty", "price", "tax", "main_image",
        #           "brand_name", "uom", "sizes"]
        fields = '__all__'


class VendorProductGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        depth = 1
        exclude = ('created_at', 'updated_at', 'soft_delete', 'vendor')

class VendorProductImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        depth = 1
        fields = "__all__"


class VendorOrderProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProductDetail
        # fields = '__all__'
        exclude = ('created_at', 'updated_at')
        depth = 2



class VendorOrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = '__all__'
        #exclude = ('created_at', 'updated_at')
        #depth = 1