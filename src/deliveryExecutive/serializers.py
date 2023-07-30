# from attr import validate
from rest_framework import serializers
from deliveryExecutive.models import DeliveryExecutive, DeliveryExeAddress, DeliveryExeBankAccount
from orders.models import DeliveryExeLiveData, OrderDetail, OrderProductDetail, VendorOrderDetails
from common.models import User

from phonenumber_field.modelfields import PhoneNumberField

class DeliveryExeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True,min_length=6)
    
class DeliveryExeChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True,min_length=6)
    new_password = serializers.CharField(required=True,min_length=6)

class DeliveryExeProfileStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryExecutive
        fields = ["status"]


class DeliveryExeProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password","is_superuser","is_staff","groups","user_permissions","role","last_login","created_at","updated_at","is_admin","is_new_user"]
    
class DeliveryExeProfileBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryExecutive
        fields = [
                "pancard",
                "pancard_doc",
                "aadhaarcard",
                "aadhaarcard_doc",
                "driving_license",
                "driving_license_doc"
            ]

# class VendorProfileBusinessSerializerUpdate(serializers.ModelSerializer):
#     org_name=serializers.CharField(max_length=50)
#     telephone_1=PhoneNumberField(blank=False, null=False, unique=True)
#     telephone_2=PhoneNumberField(blank=False, null=False, unique=True)
#     company_pancard=serializers.CharField(required=True, max_length=50)
#     company_pancard_doc=serializers.ImageField(required=False)
#     adhar_udyam_udoyog=serializers.CharField(max_length=50)
#     adhar_udyam_udoyog_doc=serializers.ImageField(required=False)
#     gst_number=serializers.CharField(max_length=50)

#     class Meta:
#         model = Vendor
#         fields = ["org_name",
#         "telephone_1",
#         "telephone_2",
#         "company_pancard",
#         "company_pancard_doc",
#         "adhar_udyam_udoyog",
#         "adhar_udyam_udoyog_doc",
#         "gst_number"]

# class VendorProfileBasicSerializerUpdate(serializers.ModelSerializer):
#     first_name = serializers.CharField(required=True)
#     last_name = serializers.CharField(required=True)
#     gender = serializers.CharField(required=False)
#     email = serializers.EmailField(required=True)
#     alternate_email = serializers.EmailField(required=False)
#     mobile = serializers.CharField(required=True)
#     profile_pic = serializers.ImageField(required=False)
    
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'gender', 'email', 'alternate_email', 'mobile', 'profile_pic']

    
class DeliveryExeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryExeAddress
        fields = ["id","DeliveryExecutive","name","address","address","locality","city","state","postcode","map_lat","map_lng"]

class DeliveryExeBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryExeBankAccount
        fields = ["id","DeliveryExecutive","acc_bank_name","acc_branch_name","acc_branch_name","acc_ifsc","acc_no","is_default"]

class DeliveryExeLiveDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryExeLiveData
        fields = "__all__"



class DeliveryExeOrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorOrderDetails
        fields = "__all__"