from rest_framework import routers
from django.urls import include, path, re_path
from CartSystem.Api import views as api_views
from CartSystem.Api import cart_views
# from CartSystem.Api import views

app_name = 'CartSystem'



router = routers.DefaultRouter()
router.register('wishlist', api_views.WishList, "cart-wishlist"),    # Method :get = View all Wishlist Product in List.
                                                                    # Method: post = Create or Add product in Wishlist
# router.register('wish-create', api_views.WishlistAddViewset, "create-wishlist"),
# router.register('wish-delete', api_views.WishlistViewSet, "delete-product-from-wishlist"),
router.register('wishlist-to-cart', api_views.WishlistToCart, "cart-wishlist-to-cart"),
router.register('wishlist-cart', api_views.WishListToCart, "wishlist-to-Cart"),  # Post Method: Product is move from wishlist to cart
# router.register('wishlist-to-cart', api_views.WishlistToCart, "cart-wishlist-to-cart"),
# router.register('add-to-cart', api_views.AddToCartViewsets, "cart-add")

# Cart urls
router.register('add-to-cart', cart_views.AddToCartViewsets, "cart-add"),# Method : post = create or Add product to cart  ---status=ok                                                                          # Method: list = View all Cart Product in List. but some not expected result only one item seen
                                                                            # method : Update = Update quantity of product
                                                                            # Method : delete = delete Product
urlpatterns = [
    # Wishlist Urls
    path("wishlist-delete/<int:pk>/", api_views.WishlistDestoryApi.as_view()),     # Delete/Remove particular product from Wishlist by wishlistid
    path('wish-create/', api_views.WishlistAdd.as_view()),                # Add Product in Wishlist
                                                                        # already another api is used for add product to wishlist

    # path('wishlist/', views.Wishlist, 'cart-wishlist'),
    # path('wish/', api_views.WishlistAll.as_view()),
    # path('wish-list/', api_views.WishListAPIView.as_view()),    # Method : get = view all wishlist Product but now not in use bocz already other used ----status:ok
    # path('wishcreate/', api_views.AddWishListApi.as_view()),
    # path('wishcre/', api_views.WishListAddApi.as_view()),
    # path('add-wishlist', api_views.add_wishlist, name='add_wishlist'),
    # path('wilist', cart_views.WishListApi.as_view()),

    # path('add-wishlist',cart_views.add_wishlist, name='add_wishlist'),

    # path("cart-delete/<int:pk>/", cart_views.CartItemDestroyApi.as_view()),
    # path("cart/", cart_views.CartItemAPIView.as_view()),
]

urlpatterns += router.urls
