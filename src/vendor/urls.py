from django.urls import path
from vendor import views

app_name = 'vendor'

urlpatterns = [

    # Vendor App Urls
    # path("order-item/<int:pk>/", views.OrderItemRetrieve.as_view()),
    # path("order-item-list/", views.OrderItemListAPIView.as_view()),
    # path("order-item/", views.CreateOrderItemApi.as_view()),
    path("vendor/registration/", views.VendorRegistrationAPIview.as_view()),
    path("vendor/login/", views.VendorLoginAPIview.as_view()),
    path("vendor/change-password/", views.VendorChangePasswordAPIview.as_view()),
    path("vendor/profile/basic/", views.VendorProfileBasicAPIview.as_view()),
    path("vendor/profile/business/", views.VendorProfileBusinessAPIview.as_view()),
    path("vendor/profile/status/", views.VendorProfileStatusAPIview.as_view()),
    path("vendor/profile/address/", views.VendorProfileAddressAPIview.as_view()),
    path("vendor/profile/bank-details/", views.VendorProfileBankDetailsAPIview.as_view()),
    path("vendor/product/", views.VendorProductDetailsAPIview.as_view()),
    path("vendor/product/images", views.VendorProductImageAPIView.as_view()),
    path("vendor/order/recent/", views.VendorOrderRecentAPIView.as_view()),
    path("vendor/order/history/", views.VendorOrderHistoryAPIView.as_view()),
    path("vendor/order/details/<int:pk>/", views.VendorOneOrderFullDetailsAPIView.as_view()),
    # path("vendor/profile/basic-update/<int:pk>", views.VendorProfileBasicUpdateAPIview.as_view()),

    path("vendor/business-summary/", views.VendorBusinessSummaryAPIView.as_view()),
    path("vendor/business-summary/sales-report/", views.SalesReportProductAPIView.as_view()),
]