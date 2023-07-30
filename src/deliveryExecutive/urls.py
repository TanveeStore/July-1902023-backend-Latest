from django.urls import path
from deliveryExecutive import views


app_name = 'deliveryExecutive'

urlpatterns = [
    #path("delivery-executive/registration/", views.VendorRegistrationAPIview.as_view()),
    path("delivery-executive/login/", views.DeliveryExeLoginAPIview.as_view()),
    path("delivery-executive/change-password/",
         views.DeliveryExeChangePasswordAPIview.as_view()),
    path("delivery-executive/profile/basic/",
         views.DeliveryExeProfileBasicAPIview.as_view()),
    path("delivery-executive/profile/business/",
         views.DeliveryExeProfileBusinessAPIview.as_view()),
    path("delivery-executive/profile/status/",
         views.DeliveryExeProfileStatusAPIview.as_view()),
    path("delivery-executive/live/location/",
         views.DeliveryExeLiveLocationData.as_view()),
    path("delivery-executive/order-list/<str:filterName>/",
         views.DeliveryExeOrderList.as_view()),
    path("delivery-executive/order-details/<int:pk>/",
         views.DeliveryExeOrderDetails.as_view()),


    path("delivery-executive/order-status-change/customer/",
         views.DeliveryExeOrdersStatusChangeForCustomer.as_view()),
    path("delivery-executive/order-status-change/vendor/",
         views.DeliveryExeOrdersStatusChangeForVendor.as_view()),


    # path("delivery-executive/profile/address/", views.VendorProfileAddressAPIview.as_view()),
    # path("delivery-executive/profile/bank-details/", views.VendorProfileBankDetailsAPIview.as_view())
]
