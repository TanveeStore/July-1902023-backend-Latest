from django.urls import path
from orders import views, order_api

from rest_framework import routers


app_name = 'orders'
urlpatterns = [

    # OrderItems Urls
    # path("order-item/<int:pk>/", views.OrderRetrieve.as_view()),
    # path("order-item-list/", views.OrderListAPIView.as_view()),
    # path("order-item/", views.CreateOrderApi.as_view()),
    # Get, Post method of Order
    path("customer/order-place/", views.OrderDetailsAPIView.as_view()),
    path("customer/order-place-razorpay/",
         views.CreateRazorpayOrder.as_view()),  # Post method of Order
    path("customer/order-place-razorpay-verify/",
         views.RazorPayVerifyPaymentAPIView.as_view()),


    # Customer Shipping Address Urls
    # get, post method of shipping address
    path("customer/shipping-address/", views.CustomerAddressAPIView.as_view()),
    # path("customer/shipping-address-delete/<int:pk>/", views.ContactAddressDeleteApiView.as_view()),
    path("customer/shipping_address-delete/<int:pk>/",
         views.DestroyContactAddressAPIView.as_view()),    # delete method of shipping address
    # update method of shipping address is working good but not used
    path("customer/shipping-address-update/<int:pk>/",
         views.UpdateContactAddressApiView.as_view()),
    # This not for front end when its need we give it.
    path("customer/order-update/<int:pk>/",
         views.OrderDetailUpdateApiView.as_view()),
    # This is urls is in use FOR GET and UPDATE using Post Method,
    path("customer/address/details/", views.UserAddressAPIview.as_view()),
    # Add new Address when any Address is not exist
    # Order Product History
    #path("customer/my-order-history/", views.OrderProductsHistoryAPIView.as_view()),

    path("customer/my-order/history/",
         views.UserOrderProductHistoryAPIView.as_view()),


     # Customer-order-return-replace-cancel
     path("customer/order/return-replace/",
          views.ReturnProductAPI.as_view()),

     # Customer-Order-return-history
     path("customer/order/return-product-history/",
          views.OrderReturnProductHistoryAPIView.as_view()),

]
