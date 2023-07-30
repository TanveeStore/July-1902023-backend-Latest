from django.contrib import admin
from CartSystem.models import WishList, AddToCart


# Register Wishlist Model
class WishListAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product']

admin.site.register(WishList, WishListAdmin)


# Register AddToCart Model
class AddToCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity']


admin.site.register(AddToCart, AddToCartAdmin)