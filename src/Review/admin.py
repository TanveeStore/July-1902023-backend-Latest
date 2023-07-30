from django.contrib import admin
from Review.models import ProductReview

# Register Product Review models.
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "comment", "rating"]
admin.site.register(ProductReview, ProductReviewAdmin)
