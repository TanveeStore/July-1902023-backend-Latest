from statistics import mode
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from common.models import User, TimeStampMixin

# Create your models here.
VendorStatus = (
    ("incomplete", "Incomplete"),
    ("inreview", "In Review"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
)


class Vendor(TimeStampMixin):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="vendor", primary_key=False)
    org_name = models.CharField("Organization Name", max_length=50)
    telephone_1 = PhoneNumberField(unique=False, blank=True, null=True)
    telephone_2 = PhoneNumberField(unique=False, blank=True, null=True)
    company_pancard = models.CharField(
        'Company Pancard(optional)', max_length=30, blank=True, null=True)
    company_pancard_doc = models.FileField(
        upload_to="documents/vendor/pancard", null=True, blank=True)
    adhar_udyam_udoyog = models.CharField(
        'Aadhaar Udyam Udoyog', max_length=200, blank=True, null=True)
    adhar_udyam_udoyog_doc = models.FileField(
        upload_to="documents/vendor/aadhaar", null=True, blank=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=VendorStatus, default="incomplete")
    distance = models.FloatField("Catering Distance(km)", blank=False, null=False, default = 0.0)

    class Meta:
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"
        ordering = ["-status"]

    def __str__(self):
        return str(self.user.first_name) + " " + str(self.user.last_name) + " | " + str(self.user.mobile) + " | " + str(self.user.email)


class VendorBankAccount(TimeStampMixin):
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, blank=False, null=False)
    acc_no = models.CharField(
        "Account No", max_length=255, blank=False, null=False)
    acc_ifsc = models.CharField(
        "IFSC Code", max_length=255, blank=False, null=False)
    acc_branch_name = models.CharField(
        "Branch Name", max_length=255, blank=False, null=False)
    acc_bank_name = models.CharField(
        "Bank Name", max_length=255, blank=False, null=False)
    is_default = models.BooleanField(
        "Default", blank=False, null=False, default=False)

    class Meta:
        verbose_name_plural = 'Vendor Accounts'

    def __str__(self):
        return str(("Vendor: {},Bank Name: {}, Branch Name: {}, IFSC: {}, Account No: {}, Default: {}").format(
            self.vendor, self.acc_bank_name, self.acc_branch_name, self.acc_ifsc, self.acc_no, self.is_default))


class VendorAddress(TimeStampMixin):
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField("Full name", max_length=255,
                            blank=False, null=False)
    address = models.CharField("Address", max_length=255,
                               help_text=("Address (Building No, Street, Area)"), blank=False, null=True)
    locality = models.CharField("Locality/Town", max_length=255)
    city = models.CharField("City/District", max_length=255,
                            help_text=("City/District"), blank=False, null=False)
    state = models.CharField("State", max_length=255,
                             help_text=("State"), blank=False, null=False)
    postcode = models.CharField(
        "Post Code", max_length=50, blank=False, null=False)
    map_lat = models.CharField(
        "Map Lat", max_length=50, blank=False, null=False)
    map_lng = models.CharField(
        "Map Lng", max_length=50, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Vendor Address'

    def __str__(self):
        return str(("Name: {}, Address: {}, Locality: {}, City: {}, State: {}, Post Code: {}").format(
            self.name, self.address, self.locality, self.city, self.state, self.postcode))
