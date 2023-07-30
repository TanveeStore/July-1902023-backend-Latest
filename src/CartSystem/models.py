from django.db import models
from common.models import User, TimeStampMixin
from products.models import Product, ProductWeight


class WishList(TimeStampMixin):
    user = models.ForeignKey(User, null=False,
                             blank=False, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    class Meta:
        verbose_name_plural = 'Wishlist'


class AddToCart(TimeStampMixin):
    user = models.ForeignKey(User, null=False,
                             blank=False, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=1)
    product_weight = models.ForeignKey(ProductWeight, null=True, blank=True, on_delete=models.CASCADE) # need to change blank and null to False


    def __str__(self):
        return str("Quantity: {}, Product: {} - Rs. {}".format(self.quantity or '',
                                                                         self.product.name,
                                                                         (self.product_weight.price - self.product_weight.discount_price ) * self.quantity))
    def cartTotal(self):
        total = (self.product) * self.quantity
        return total

    class Meta:
        verbose_name_plural = 'Add To Cart'

    def get_user_name(self):
        return self.user.first_name + '' + self.user.last_name