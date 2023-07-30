from django.db.models import Q
from CartSystem.models import WishList, AddToCart
import decimal
from CartSystem.serializers import CartItemSerializer


def get_wishlist_by_user(request):
    """
        Quantity:   If empty, then unlimited
                    If 0, finished
                    If >0, show the quantity
    """
    # user = request.user.id
    # user = request.query_params.get('user')
    # print(user)
    # wishlists = WishList.objects.filter(user=user)
    wishlists = WishList.objects.filter(user=request.user)
    print(wishlists)
    wishlist_data = []
    print(wishlist_data)
    for data in wishlists:

        wishlist_data.append({
            "id": data.id,
            "ProductId" : data.product.id,
            "ProductName": data.product.name,
            "ShortDescription": data.product.short_description,
            "price": data.product_weight.price,
            "discount_price": (data.product_weight.price - data.product_weight.discount_price),
            "mainImage": request.build_absolute_uri(data.product.main_image.url),

        })
    return wishlist_data


def check_whislist(request, product):
    # user = request.query_params.get('user')
    try:
        cart = WishList.objects.get(
            Q(product=product) & Q(user=request.user))
        print(cart)
        return True
    except (Exception, WishList.DoesNotExist):
        return False


def delete_from_wishlist(request, pk):
    try:
        wishlist = WishList.objects.get(pk=pk)
        print(wishlist)
        if request.user == wishlist.user:
            print(wishlist.user)
            wishlist.delete()
            return True
    except (WishList.DoesNotExist, Exception) as e:
        return False

    return False


def get_user_cart(request):
    if request.user.is_authenticated:
        print(request.user)
        cart = AddToCart.objects.filter(user=request.user)
        # cart_data = CartItemSerializer(cart).data
        # print("cart_data",cart_data)
        data = []
        total = 0
        if cart:
            print(12345678, cart)
            for item in cart:
                print(1111,item.product_weight)
                if not item.product.soft_delete and item.product.status:
                    print("polkiju")
                    total_price = item.quantity * (item.product_weight.price - item.product_weight.discount_price)
                    total += total_price
                    if item.quantity > 0:
                        data.append({
                            "id": item.id,
                            "productName": item.product.name,
                            "weight": (item.product_weight.weight),
                            "uom1": item.product_weight.uom.short_name,
                            "price": item.product_weight.price,
                            "discount_price": (item.product_weight.price - item.product_weight.discount_price),
                            "tax" : item.product.tax,
                            "quantity": item.quantity,
                            "mainImage": request.build_absolute_uri(item.product.main_image.url),
                            "totalPrice": total_price,
                            "sizeId": item.product_weight.id,
                            "productId": item.product.id
                            # "cart_id": cart.
                        })
                else:
                    item.delete()
        print(data, total, "polkjh")
        return data, total


def check_cart(request, product):
    try:
        cart = AddToCart.objects.get(
            Q(product=product) & Q(user=request.user))
        return True
    except (Exception, AddToCart.DoesNotExist):
        return False


def delete_from_cart(request, pk):
    try:
        cart = AddToCart.objects.get(pk=pk)
        print(cart)
        if request.user == cart.user:
            cart.delete()
            return True
    except (AddToCart.DoesNotExist, Exception) as e:
        return False

    return False


def get_cart_amt_detail(request):
    if request.user.is_authenticated:
        cart = AddToCart.objects.filter(user=request.user)

        returnData={}
        returnData["cartAmt"] = 0
        returnData["cartTaxAmt"] = 0
        returnData["cartDeliveryAmt"] = 0
        returnData["cartNoOfProducts"] = 0
        # sum_of_total_quantity
        returnData["totalCartProductQty"] = 0
        if cart:
            for item in cart:
                if not item.product.soft_delete and item.product.status:
                    returnData["cartAmt"] += decimal.Decimal(item.quantity * (item.product.price-item.product.discount_price))
                    returnData["cartTaxAmt"] +=decimal.Decimal((item.quantity*(item.product.price-item.product.discount_price)))*item.product.tax/100
                    returnData["totalCartProductQty"] += item.quantity
                    returnData["cartNoOfProducts"] +=1


    return returnData

def deleteCartAllProducts(request):
    try:
        cart = AddToCart.objects.filter(user=request.user)
        cart.delete()
        return True
    except AddToCart.DoesNotExist:
        return False
