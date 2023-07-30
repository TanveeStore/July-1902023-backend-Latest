from django.urls import path
from Offers import views



app_name = 'Offers'
urlpatterns = [

    path("offer/offer-list/", views.OfferApiView.as_view()),
    # path('offer/offer-create/', views.OfferApiView.as_view()),
    path('offer/offer/<int:pk>', views.OfferCouponApiView.as_view()),
    path("offer/apply/", views.ApplyOfferCouponAPIView.as_view()),

]