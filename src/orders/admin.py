from django.contrib import admin
from orders.models import OrderDetail, ContactAddress, OrderProductDetail, VendorOrderDetails, ReturnProduct

# admin.site.register(OrderNumber)

# Register ContactAddress Model
class ContactAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', "user", "address_line", "map_lat", "map_lng"]
    list_display_links = ["id", "name", "user", "address_line"]
    search_fields = ["user__first_name", "user__last_name", "name", "contact_number"]
    # list_filter = ["user", "name"]
admin.site.register(ContactAddress, ContactAddressAdmin)


# Register OrderDetail
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ["id",
                    "order_number",
                    "address",
                    "price",
                    "shipping_charge",
                    "tax",
                    "totalOrderdQty",
                    "offer_discount",
                    "grand_total",
                    "payment_method",
                    "payment_status",
                    "delivery_exe",
                    "order_status",
                    "userRemark",
                    "created_at"]
    list_display_links = ["id", "order_number"]
    list_filter = ["payment_method", "payment_status", "order_status"]
    search_fields = ["id", "order_number", "grand_total", "payment_method", "payment_status", "order_status", "delivery_exe__user__first_name", "delivery_exe__user__last_name"]
    list_per_page = 15
admin.site.register(OrderDetail, OrderDetailAdmin)


# Register OrderProductDetail Model
class OrderProductDetailAdmin(admin.ModelAdmin):

    list_display = ["id",
                    "order",
                    "product",
                    "price",
                    "quantity",
                    "taxRate",
                    "total_price",
                    "created_at",
                    ]
    list_display_links = ["id","order"]
    list_filter = ["order"]
    search_fields = ["id", "product__name", "order__order_number", "price", "total_price"]
    list_per_page = 15
admin.site.register(OrderProductDetail, OrderProductDetailAdmin)


# Register VendorOrderDetails Model
# Register OrderProductDetail Model
class VendorOrderDetailsAdmin(admin.ModelAdmin):

    list_display = ["id",
                    "order",
                    "vendor",
                    "total_items",
                    "total_quantity",
                    "total_price",
                    "total_tax",
                    "grand_total",
                    "order_status",
                    ]
    list_display_links = ["id","order", "vendor"]
    list_filter = ["order", "vendor"]
    search_fields = ["id", "order__order_number", "vendor__user__first_name","vendor__user__last_name", "vendor__org_name"]
    list_per_page = 15
admin.site.register(VendorOrderDetails, VendorOrderDetailsAdmin)


# Register ReturnProduct Model
class ReturnProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'orderNumber', "orderedProduct", "return_id", "returnQty", "userRemarkStatus", "refundAmt", "adminRemarkStatus"]
    list_display_links = ["id", "orderNumber"]
    search_fields = ["orderNumber", "return_id"]
    # list_filter = ["user", "name"]
admin.site.register(ReturnProduct, ReturnProductAdmin)
