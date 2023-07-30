from django.db import models
from common.models import User, TimeStampMixin
from products.models import Product

RATING=(
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
)


# Product Review Model
class ProductReview(TimeStampMixin):
    user = models.ForeignKey(User, null=False,
                             blank=False, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000, blank=True, null=True)
    rating = models.CharField(choices=RATING, max_length=150)

    def __str__(self):
        return str(self.user.first_name) + " " + str(self.user.last_name)

    class Meta:
        verbose_name_plural = 'Product Review'


