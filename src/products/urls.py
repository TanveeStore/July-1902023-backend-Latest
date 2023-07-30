from django.urls import path
from products import views


app_name = 'products'

urlpatterns = [
    # Category Urls
    path("category-list/", views.CategoryListApiView.as_view()),  # This Api is Category List.
    # path("category-create/", views.CategoryCreateAPIView.as_view()),
    path("category/<int:pk>/", views.CategoryAPIView.as_view()),
    # path("category-delete/<int:pk>/", views.CategoryDestoryAPIView.as_view()),
    # path("category-update/<int:pk>/", views.CategoryUpdateAPIView.as_view()),
    # path('category', views.CategoryInfo, "category-info"),
    path('products', views.ProductByLocationAPIView.as_view()),    # http://127.0.0.1:8000/api/products?category=id
                                                      # GET /api/products?category=id
    # path('products-location/', views.ProductByLocationAPIView.as_view()),     # by location

    # path('category-product-list', views.CategoryProductList.as_view()),
    # path("category/<id>/", views.ProductsByCategory.as_view(), name="product-category-list"),
    # path('brand-product-list/<int:brand_name_id>', views.brand_product_list, name='brand-product-list'),
    path('products-brand', views.ProductbyBrandView.as_view()),

    # Brand urls
    path("product/brand-list/", views.BrandListApiView.as_view()),

    # Unit of Measure Urls
    path("product/unit_of_measure/<int:pk>", views.UoMAPIView.as_view()),
    path("product/unit-of-measure-list/", views.UoMAPIListApiView.as_view()),

    # Size Urls
    path("product/size-list/", views.SizeAPIView.as_view()),

    # Product Urls
    path("item-list/", views.ProductListAPIView.as_view()),
    path("product/<int:pk>", views.ProductRetrieveView.as_view()),
    path("product/images/<id>/", views.ProductImagesByProductId.as_view(), name="product-images-filter"),
    path("product/search", views.ProductBySearchAPIView.as_view())
]
