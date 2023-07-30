from django.urls import path
from Review import views


app_name = 'Review'

urlpatterns = [

    # OrderItems Urls
    path("customer/product-review/", views.ProductReviewApi.as_view()),                # get, post method for Product Review
    path("customer/product-review/<int:pk>/", views.DestroyProductReviewAPIView.as_view()),    # delete method for Product Review


]