from django.urls import path
from checkout import views



app_name = 'checkout'
# urlpatterns = [
#     # path('process/',views.CreateOrder.as_view(), name="process"),
#     path("customer/order-payment/create/", views.RazorPayCreatePaymentAPIView.as_view()),
#     path("customer/order-payment/verify/", views.RazorPayVerifyPaymentAPIView.as_view()),

# ]

urlpatterns = [
    path("customer/order-payment/create/", views.RazorPayCreatePaymentAPIView.as_view()),
    path("customer/order-payment/verify/", views.RazorPayVerifyPaymentAPIView.as_view()),

]