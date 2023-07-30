from __future__ import unicode_literals
from common.models import User, Profile, Address, BankDetails
from django.contrib import admin

# from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# admin.site.register(MobileOTP)
admin.site.register(Address)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "address", "role", "otp"]
admin.site.register(Profile, ProfileAdmin)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id', 'first_name', 'last_name', 'email', 'mobile', 'role','date_joined','fcm_token', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'is_admin', "is_superuser")
    '''search_fields = ('mobile', 'first_name', 'last_name')
    ordering = ('mobile', '-is_active')
    filter_horizontal = ()'''
    fieldsets = (
        (None, {'fields': ('mobile', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
                                      'email', 'gender', 'role', 'profile_pic')}),
        ('Permissions', {'fields': ('is_superuser','is_admin', 'is_staff', 'is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2')}
         ),
    )

    search_fields = ('email', 'mobile', 'first_name', 'last_name')
    ordering = ('mobile', '-is_active')
    filter_horizontal = ()
    list_per_page = 10
    inlines = (ProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

admin.site.register(User, UserAdmin)


# BankDetails Model register
class BankDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'acc_no', 'acc_ifsc', 'acc_branch_name','acc_bank_name','branchCode', 'is_default', 'created_at')
    search_fields = ('name', 'id')
    list_display_links = ('id', 'user')
admin.site.register(BankDetails, BankDetailsAdmin)
