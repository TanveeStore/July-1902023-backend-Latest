from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from common.models import User, TimeStampMixin


# Create your models here.
DeliveryExeStatus = (
    ("active", "Active"),
    ("inactive", "Inactive"),
    ("blocked", "Blocked"),
)


class DeliveryExecutive(TimeStampMixin):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="delivery", primary_key=False)
    pancard = models.CharField('Pan', max_length=30, blank=True, null=True)
    pancard_doc = models.FileField(
        upload_to="documents/deliveryExecutive/panCard", null=True, blank=True)
    aadhaarcard = models.CharField(
        'Aadhaar', max_length=200, blank=True, null=True)
    aadhaarcard_doc = models.FileField(
        upload_to="documents/deliveryExecutive/aadhaarCard", null=True, blank=True)
    driving_license = models.CharField(max_length=20, blank=False, null=False)
    driving_license_doc = models.FileField(
        upload_to="documents/deliveryExecutive/drivingLicense", null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=DeliveryExeStatus, default="active")

    class Meta:
        verbose_name = "Delivery Executive"
        verbose_name_plural = "Delivery Executives"
        ordering = ["-status"]

    def __str__(self):
        return str(self.user.first_name) + " " + str(self.user.last_name) + " | " + str(self.user.mobile) + " | " + str(self.user.email)


class DeliveryExeBankAccount(TimeStampMixin):
    delivery_exe = models.OneToOneField(
        DeliveryExecutive, on_delete=models.CASCADE, primary_key=False)
    acc_no = models.CharField(
        "Account No", max_length=255, blank=False, null=False)
    acc_ifsc = models.CharField(
        "IFSC Code", max_length=255, blank=False, null=False)
    acc_branch_name = models.CharField(
        "Branch Name", max_length=255, blank=False, null=False)
    acc_bank_name = models.CharField(
        "Bank Name", max_length=255, blank=False, null=False)
    is_default = models.BooleanField(
        "Default", blank=False, null=False, default=True)

    class Meta:
        verbose_name_plural = 'Delivery Exe. Banks'

    def __str__(self):
        return str(self.delivery_exe)


class DeliveryExeAddress(TimeStampMixin):
    delivery_exe = models.OneToOneField(
        DeliveryExecutive, on_delete=models.CASCADE, primary_key=False)
    address = models.CharField("Address", max_length=255,
                               help_text=("Address (Building No, Street, Area)"), blank=False, null=True)
    locality = models.CharField("Locality/Town", max_length=255)
    city = models.CharField("City/District", max_length=255,
                            help_text=("City/District"), blank=False, null=False)
    state = models.CharField("State", max_length=255,
                             help_text=("State"), blank=False, null=False)
    postcode = models.CharField(
        "Post Code", max_length=50, blank=False, null=False)
    map_lat = models.CharField("Map Lat", max_length=50, blank=True, null=True)
    map_lng = models.CharField("Map Lng", max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Delivery Exe. Address'

    def __str__(self):
        return str(self.delivery_exe)
