from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from common.models import User, Profile, Address, BankDetails
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
#from common.core.validators import validate_user
from django.utils.encoding import smart_str, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
import logging

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('mobile', 'password', 'email', 'username')
        extra_kwargs = {'password': {'write_only': True},
                        'email' : {'write_only': True},
                        'username' : {'write_only' : True},}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# User for Order or other Module
class CommonUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "alternate_email",
            "mobile",
            "profile_pic",
        )


# used for giving in the login and update user profile
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("id", "password", "last_login", "created_at", "updated_at",
                    "is_new_user", "is_superuser", "is_staff", "is_admin")


    def validate(self, attrs):
        mobile = attrs.get('mobile')
        if mobile:
            if User.objects.filter(mobile=mobile).exists():
                if User.objects.filter(mobile=mobile).count() > 1:
                    msg = {'detail': 'mobile number is already associated with another user. Try a new one.', 'status':False}
                    raise serializers.ValidationError(msg)

        return attrs


    def update(self, instance, validated_data):
        instance.mobile = validated_data['mobile']
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.email = validated_data['email']
        # instance.alternate_email =  validated_data['alternate_email']
        #instance.username = validated_data['username']
        #instance.profile_pic = validated_data['profile_pic']

        instance.save()
        return instance
    
class LoginWithMobileUserSerializer(serializers.Serializer):
    mobile = serializers.CharField(min_length=13, max_length=13)


class LoginUserSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)


    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone and password:
            if User.objects.filter(phone=phone).exists():
                user = authenticate(request=self.context.get('request'), phone=phone, password=password)

            else:
                msg = {'detail': 'Phone number is not registered.','register': False}
                raise serializers.ValidationError(msg)
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class AddressSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.get_country_display()

    class Meta:
        model = Address
        fields = ("address_line", "street", "city",
                  "state", "postcode", "country")

    def __init__(self, *args, **kwargs):
        account_view = kwargs.pop("account", False)

        super(AddressSerializer, self).__init__(*args, **kwargs)

        if account_view:
            self.fields["address_line"].required = True
            self.fields["street"].required = True
            self.fields["city"].required = True
            self.fields["state"].required = True
            self.fields["postcode"].required = True
            self.fields["country"].required = True


class CreateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            "role",
        )

    def __init__(self, *args, **kwargs):
        super(CreateProfileSerializer, self).__init__(*args, **kwargs)
        self.fields["role"].required = True


class ProfileSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()
    address = AddressSerializer()

    def get_user_details(self, obj):
        return UserSerializer(obj.user).data

    class Meta:
        model = Profile
        exclude = ('otp', 'count',)
        # fields = ("id", 'user_details', 'role', 'address')


# Logout Serializer
class UserLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']

        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            # msg = {"message": "Bad request. Refresh Token is required"}
            self.fail("Bad request. Invalid refresh token")
        
        """try:
            assert False == True
            try:
                RefreshToken(self.token).blacklist()
            except TokenError:
                #msg = {"message": "Bad request. Refresh Token is required"}
                return Response(self.fail("Bad request. Invalid refresh token"))
        except AssertionError:
            return Response(logging.error("Something went to wrong!", exc_info=True))"""
class LogoutSerializer(serializers.Serializer):
    refreshToken = serializers.CharField(required=True)
    accessToken = serializers.CharField(required=True)

class UserAccountLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']

        return attrs


class ResentOtpSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField(help_text=("Mobile"), required=True)

    class Meta:
        model = User
        fields = ('mobile',)

class UpdateAddressSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.get_country_display()

    class Meta:
        model = Address
        fields = ("address_line", "street", "city",
                  "state", "postcode", "country")

    def __init__(self, *args, **kwargs):
        account_view = kwargs.pop("account", False)

        super(UpdateAddressSerializer, self).__init__(*args, **kwargs)

        if account_view:
            self.fields["address_line"].required = True
            self.fields["street"].required = True
            self.fields["city"].required = True
            self.fields["state"].required = True
            self.fields["postcode"].required = True
            self.fields["country"].required = True
    # class Meta:
    #     model = Address
    #     fields = ("address_line", "street", "city",
    #               "state", "postcode", "country")

class UserCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", "is_superuser", "is_staff", "groups", "user_permissions", "role",
                   "last_login", "created_at", "updated_at", "is_admin", "is_new_user"]


class UpdateProfileSerializer(serializers.ModelSerializer):
    #address = UpdateAddressSerializer()


    class Meta:
        model = Profile
        exclude = ('otp', 'role', 'user')
        #fields = ('address',)


class UserProfileBasicSerializerUpdate(serializers.ModelSerializer):
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

class GoogleLoginSerializer(serializers.Serializer):
    idToken = serializers.CharField(required=True)


class FacebookLoginSerializer(serializers.Serializer):
    accessToken = serializers.CharField(required=True)


class UserCommonSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# Forgot Password
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=200)

    def validate(self, data):
        email = data.get("email")
        user = User.objects.filter(email__iexact=email).last()
        if not user:
            raise serializers.ValidationError(
                "You don't have an account. Please create one."
            )
        return data


# Reset Password
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not default_token_generator.check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)


# BankDetailsSerializer
class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = "__all__"
