from rest_framework import serializers
from products.models import Product, Category, ProductImage, Size, Brand, UnitofMeasure, ProductWeight
# Category Serializer
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        # fields = '__all__'            # all Category models field(data)
        exclude = ('created_at', 'updated_at')   # exclude these fields and show all data.


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        # fields = '__all__'                        # all Brand models field(data)
        exclude = ('created_at', 'updated_at')       # exclude these fields and show all data.


# UnitOfMeasure Serializer
class UoMSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnitofMeasure
        # fields = '__all__'                      # all Uom models field(data)
        exclude = ('created_at', 'updated_at')  # exclude these fields and show all data.

# Size Serializer
class SizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Size
        # fields = '__all__'                     # all Uom models field(data)
        exclude = ('created_at', 'updated_at')    # exclude these fields and show all data.

class ProductWeightSerializer(serializers.ModelSerializer):
    uom = UoMSerializer()
    class Meta:
        model = ProductWeight
        fields = '__all__'
# Product Serializer
class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer()       # serialize the category fields of Product Model
    brand_name = BrandSerializer()
    uom = UoMSerializer()  # serialize the uom fields of Product Model
    sizes = SizeSerializer()

    # serialize the brand fields of Product Model                 # serialize the size_type fields of Product Model
    class Meta :
        model = Product
        # fields = '__all__'                                         # all Product models field(data)
        exclude = ('created_at', 'updated_at', 'soft_delete')         # exclude these fields and show all data.


class ProductImageSerializer(serializers.ModelSerializer):


    class Meta:
        model = ProductImage
        fields = ["id", "product", "image"]                    # all ProductImage models field(data)
        # exclude = ('created_at', 'updated_at')                    # exclude these fields and show all data.


class ProductSingleSerializer(serializers.ModelSerializer):
     class Meta :
         model = Product
         exclude = ('created_at', 'updated_at', 'description', 'category', 'sizes', 'brand_name', 'uom',
                    'soft_delete')
