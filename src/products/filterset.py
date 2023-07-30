from django_filters import rest_framework as filters
from products.models import Product, Category


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name', 'category__name', 'brand_name__name', 'min_price', 'max_price']
        # fields = ['category', 'brand_name', 'min_price', 'max_price']