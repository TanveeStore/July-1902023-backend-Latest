from django.urls import path
from Dashboard import views



app_name = 'Dashboard'

urlpatterns = [

    # Popular wishlist Product
    path("dashboard/popular/wishlist-product/", views.PopularProductInWishListAPIView.as_view()),

    # Popular Cart Product
    path("dashboard/popular/cart-product/", views.PopularProductInCartAPIView.as_view()),

    # Popular Ordered Product
    path("dashboard/popular/ordered-with-location-product/", views.PopularOrderedProductAPIView.as_view()),
    
    path("dashboard/popular/ordered-product/", views.PopularOrderedProductWitoutLocationAPIView.as_view()),

    # Fresh Arrivals Product
    path("dashboard/fresh/arrival-products/", views.FreshArrivalProductAPIView.as_view()),

    # Fresh Arrivals Product
    # path("dashboard/fresh/arrival-with-location-products/", views.FreshArrivalProductWithLocationAPIView.as_view()),
]
