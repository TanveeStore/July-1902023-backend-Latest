from django.contrib import admin
from products.models import Product, Category, Brand, Size, UnitofMeasure, ProductImage, ProductWeight

# Register ProductImage models here.
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5
    readonly_fields = ['image_tag']

# Register Category Model
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_filter = ['name',]
    list_per_page = 10
    search_fields = ['name']
    readonly_fields = ['image_tag',]

admin.site.register(Category, CategoryAdmin)


# Register Product Model
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'category', "tax", 'short_description', 'vendor'
    ]
    list_display_links = ['id', 'name']
    inlines = [ProductImageInline, ]
    list_filter = ['category', 'vendor']
    list_per_page = 10
    search_fields = ['name', 'category__name', 'vendor__org_name']
admin.site.register(Product, ProductAdmin)

# Register Brand, Size, UnitofMeasure Models, ProductImages
admin.site.register(Brand)

class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ["id", "size"]
admin.site.register(Size, ProductSizeAdmin)

class ProductUnitofMeasureAdmin(admin.ModelAdmin):
    list_display = ["id", "name","short_name"]
admin.site.register(UnitofMeasure, ProductUnitofMeasureAdmin)

class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", "product", 'image']
admin.site.register(ProductImage, ProductImageAdmin)

class ProductWeightAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "weight", "qty", "price"]
admin.site.register(ProductWeight, ProductWeightAdmin)
