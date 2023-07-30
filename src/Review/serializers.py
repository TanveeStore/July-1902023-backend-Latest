from rest_framework import serializers
from Review.models import ProductReview
from orders.models import OrderProductDetail

# serializer for Product Review models
class ProdcutReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductReview
        fields = ['product', 'comment', 'rating']

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductReview
        fields = "__all__"

