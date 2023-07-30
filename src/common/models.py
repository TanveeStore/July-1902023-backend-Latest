from __future__ import unicode_literals
from django.db import models
import datetime
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from common.utils import ROLES, GENDER_CHOICES, COUNTRIES
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
import random
from django.db.models.signals import post_save
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    def create_user(self, email, mobile, password=None):
        """
        Creates and saves a User with the given email, first_name, last_name, mobile
        and password.
        """
        if not mobile:
            raise ValueError('User must have a mobile number')

        if not password:
            raise ValueError('User must have a password')

        user = self.model(
            email=self.normalize_email(email),
            mobile=mobile,
        )

        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        # user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email,  mobile, password=None):
        """
        Creates and saves a User with the given email, mobile
        and password
        """
        user = self.create_user(
            email,
            password=password,
            mobile=mobile,
        )
        user.is_staff = True
        # user.is_admin = True
        user.is_superuser = True
        # user.is_active=True
        user.save(using=self._db)
        return user


class TimeStampMixin(models.Model):
    """Class representing the created_at and updated_at fields declared
    globally"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """This model will not create any Database Table"""
        abstract = True


# Create Custom User models.
class User(AbstractBaseUser, PermissionsMixin, TimeStampMixin):

    #username = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=20, blank=False, null=False)
    last_name = models.CharField(max_length=20, blank=False, null=False)
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, null=False, blank=False)
    # Email field that serves as the username field
    email = models.EmailField(
        max_length=100, unique=True, blank=True, null=True)
    alternate_email = models.EmailField(max_length=100, null=True, blank=True)
    mobile = PhoneNumberField(
        'Mobile number', max_length=15, blank=False, null=False, unique=True)
    # account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='users')
    is_active = models.BooleanField(default=True)

    """If the user account is active or not. Defaults to True.
        If the value is set to false,user will not be allowed to sign in."""
    is_admin = models.BooleanField(default=False)
    is_new_user = models.BooleanField(default=True)
    date_joined = models.DateTimeField('date joined', auto_now_add=True)
    role = models.CharField(max_length=50, choices=ROLES, default='user')
    profile_pic = models.FileField(
        upload_to="profile_pic", null=True, blank=True)
    is_superuser = models.BooleanField(
        ('superuser status'),
        default=False,
        help_text=(
            'Designates whether the user can log into this admin'
            ' site.',
        ),
    )
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=(
            'Designates whether the user can log into this admin'
            ' site.',
        ),
    )

    is_verified = models.BooleanField(
        null=False, blank=False, default=False)  # False = not verified
    google_id = models.CharField(max_length=255, null=True, blank=True)
    facebook_id = models.CharField(max_length=255, null=True, blank=True)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)

    # Setting email instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile']

    # the default UserManager to make it work with our custom User Model
    objects = UserManager()

    def get_full_name(self):
        # Returns the first_name plus the last_name, with a space in between.
        full_name = None
        if self.first_name or self.last_name:
            full_name = self.first_name + " " + self.last_name
        # elif self.username:
        #     full_name = self.username
        else:
            full_name = self.email
        return full_name

    # def get_short_name(self):
    #     # Returns the short name for the user.
    #     return self.username

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name) + " | " + str(self.mobile)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    """@property
    def is_staff(self):
        return True

    @property
    def is_admin(self):
        return True

    @property
    def is_active(self):
        return True"""

    '''@property
    def is_staff(self):
        "Is the user a member of staff"
        # Simplest possible answer : All admins are staff
        return self.is_admin'''

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User'


# Create Address models here.
class Address(models.Model):
    address_line = models.CharField(
        "Address", max_length=255, blank=True, null=True)
    street = models.CharField("Street", max_length=55, blank=True, null=True)
    city = models.CharField("City", max_length=255, blank=True, null=True)
    state = models.CharField("State", max_length=255, blank=True, null=True)
    postcode = models.CharField(
        "Post/Zip-code", max_length=64, blank=True, null=True)
    country = models.CharField(
        max_length=3, choices=COUNTRIES, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Address'

    def __str__(self):
        return str(("Address line: {}, street: {}, City: {}, State: {}, Post Code: {}").format(
            self.address_line, self.street, self.city, self.state, self.postcode))

    # def get_complete_address(self):
    #     address = ""
    #     if self.address_line:
    #         address += self.address_line
    #
    #     if self.street:
    #         if address:
    #             address += ", " + self.street
    #         else:
    #             address += self.street
    #     if self.city:
    #         if address:
    #             address += ", " + self.city
    #         else:
    #             address += self.city
    #     if self.state:
    #         if address:
    #             address += ", " + self.state
    #         else:
    #             address += self.state
    #     if self.postcode:
    #         if address:
    #             address += ", " + self.postcode
    #         else:
    #             address += self.postcode
    #
    #     if self.country:
    #         if address:
    #             address += ", " + self.get_country_display()
    #         else:
    #             address += self.get_country_display()
    #     return address


class Profile(models.Model):

    user = models.OneToOneField(User, related_name='profile',
                                on_delete=models.CASCADE)   # 1 to 1 link with Django User
    address = models.ForeignKey(
        Address, on_delete=models.CASCADE, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLES,
                            null=True, default='user')
    otp = models.CharField(max_length=6, blank=True, null=True)
    # count = models.IntegerField(default=0, help_text='Number of otp sent')

    def __str__(self):
        return str(self.user)


'''
def user_created_receiver(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user = instance)
post_save.connect(user_created_receiver, sender = User)
'''


'''class MobileOTP(models.Model):
    mobile = PhoneNumberField('Mobile number', blank=True, null=True, unique=True)
    otp = models.CharField(max_length = 6, blank = True, null= True)
    count = models.IntegerField(default = 0, help_text = 'Number of otp sent')
    logged = models.BooleanField(default = False, help_text = 'If otp verification got successful')
    forgot = models.BooleanField(default = False, help_text = 'only true for forgot password')
    forgot_logged = models.BooleanField(default = False, help_text = 'Only true if validate otp forgot get successful')


    def __str__(self):
        return str(self.mobile) + ' is sent ' + str(self.otp) '''


# Customer Bank Details
class BankDetails(TimeStampMixin):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    name = models.CharField("Account Holder Name", max_length=300, blank=False, null=False)
    acc_no = models.CharField(
        "Account No", max_length=255, blank=False, null=False)
    acc_ifsc = models.CharField(
        "IFSC Code", max_length=255, blank=False, null=False)
    acc_branch_name = models.CharField(
        "Branch Name", max_length=255, blank=False, null=False)
    acc_bank_name = models.CharField(
        "Bank Name", max_length=255, blank=False, null=False)
    branchCode = models.CharField("Branch Code", max_length=20, blank=False, null=False)
    is_default = models.BooleanField(
        "Default", blank=False, null=False, default=False)


    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Bank Details'
        