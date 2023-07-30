from django.urls import include, path

app_name = "common_urls"

urlpatterns = [
    path("", include(("common.urls"))),
    path("", include(('products.urls'))),
    path("", include(('CartSystem.Api.urls'))),
    path("", include(('orders.urls'))),
    path("", include(('Review.urls'))),
    path("", include(('Offers.urls'))),
    path("", include(('vendor.urls'))),
    path("", include(('deliveryExecutive.urls'))),
    path("", include(("checkout.urls"))),
    path("", include(("Dashboard.urls"))),
    path("", include(("Notifications.urls"))),
    path("", include(("Wallet.urls"))),
]