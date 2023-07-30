from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, mixins, status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,  ListCreateAPIView, CreateAPIView, DestroyAPIView
from products.models import Product, ProductWeight
from products.serializers import ProductSerializer
from CartSystem.common import cart_system as cart_helper
from CartSystem.serializers import WishlistSerializer, AddToCartSerializer, AddToWishlistSerializer, CartItemSerializer
from CartSystem.models import AddToCart, WishList
from rest_framework.views import APIView
from common.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotAcceptable, ValidationError, PermissionDenied


class WishListApi(APIView):

    """ API for Product """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.query_params.get('user')
        # wishlist = cart_helper.get_wishlist_by_user(request)
        if user:
            queryset = WishList.objects.filter(user__id=user)
            print(queryset)
        else:
            queryset = WishList.objects.all()
        serializer = WishlistSerializer(queryset, many=True)
        return Response({'count': len(serializer.data),
                         'data': serializer.data,
                         })

# 'data' : serializer.data,


# Wishlist
'''def add_wishlist(request):
	pid = request.GET['product']
	product = Product.objects.get(pk=pid)
	data={}
	checkw = WishList.objects.filter(product=product, user=request.user).count()
	if checkw > 0:
		data={
			'bool': False
		}
	else:
		wishlist = WishList.objects.create(
			product=product,
			user=request.user
		)
		data= {
			'bool': True
		}
	return JsonResponse(data)'''

# My Wishlist


def my_wishlist(request):
    wlist = WishList.objects.filter(user=request.user).order_by('-id')
    return Response(request, {'wlist': wlist})


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        pass


# Add, Delete, Update Product To Cart  and  list of Cart Product API
class AddToCartViewsets(viewsets.ModelViewSet):
    queryset = AddToCart.objects.none()
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        try:
            try:
                quantity = request.data['quantity']
                productId = request.data['product']  # id=product.id
                weightId = request.data['sizeId']
                print(quantity, productId, weightId, 8765)

            except Exception:
                return Response({"data": {"msg": "Data is missing. Please try again."}}, status=status.HTTP_400_BAD_REQUEST)

            try:
                product = Product.objects.get(
                    id=productId)
            except (Product.DoesNotExist, Exception) as e:
                return Response({"data": {"message": "Product not found."}}, status=status.HTTP_404_NOT_FOUND)

            try:
                product_weight = ProductWeight.objects.get(id=weightId)

            except (ProductWeight.DoesNotExist, Exception) as e:
                return Response({"data": {"message": "Select weight for the Product not found."}}, status=status.HTTP_404_NOT_FOUND)

            if not cart_helper.check_cart(request, product, product_weight):
                print(userObj, product, quantity, product_weight)
                cart = AddToCart.objects.create(
                    user=userObj, product=product, quantity=quantity, product_weight=product_weight)

                return Response({"data": {"message": "Product added to cart."}}, status=status.HTTP_201_CREATED)
            else:
                cartObj = AddToCart.objects.get(user=userObj, product=product, product_weight=product_weight)
                # for i in
                cartObj.quantity = quantity
                cartObj.save()
                return Response({"data": {"message": "Product updated in cart."}}, status=status.HTTP_200_OK)
                # return Response({"data": {"message": "Product available in cart."}}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception:
            return Response({"data": {"message": "Something went wrong. Please try again."}}, status=status.HTTP_409_CONFLICT)

    def list(self, request):
        cart = cart_helper.get_user_cart(request)
        if len(cart[0]) > 0:
            return Response({"status": "success", "data": {"cartItem": cart[0], "grandTotal": cart[1]}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "warning", "message": "Cart is empty!", "data":{"cartItem":[], "grandTotal": 0}}, status=status.HTTP_200_OK)

    def update(self, request,pk):
        try:
            cart = AddToCart.objects.get(pk=pk)
            cart.quantity = request.data['quantity']
            cart.save()
            updated_cart = cart_helper.get_user_cart(request)
            data = {
                "totalPrice": (cart.product_weight.price - cart.product_weight.discount_price) * int(cart.quantity),
                "grandTotal": updated_cart[1],
                "msg": "Cart Updated."
            }
            return Response({"data": data}, status=status.HTTP_200_OK)
        except (AddToCart.DoesNotExist, Exception) as e:
            return Response({"data": {"message": "Cart not found. Please try again."}}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk):
        userObj = User.objects.get(id=self.request.user.id)
        try:
            weight_id = request.data['sizeId']
            product_id = request.data['product']
            cart_id = request.data['cartId']
            product_weight = ProductWeight.objects.get(id=weight_id)
            if cart_id == 'nun':
                cartObj = AddToCart.objects.get(user=userObj, product=product_id, product_weight=product_weight)
                cartObj.quantity = 0
                cartObj.save()
                data = {
                    "grandTotal": [],
                    "msg": "Item deleted from the cart."
                }
            else:
                AddToCart.objects.get(product=product_id, product_weight=product_weight, pk=cart_id).delete()
                updated_cart = cart_helper.get_user_cart(request)
                data = {
                    "grandTotal": updated_cart[1],
                    "msg": "Item deleted from the cart."
                }

            return Response({"data": data}, status=status.HTTP_200_OK)
        except (Exception, AddToCart.DoesNotExist):
            return Response({"data": {"message": "Cart not found."}}, status=status.HTTP_404_NOT_FOUND)


'''class CartItemDestroyApi(DestroyAPIView):

    queryset = AddToCart.objects.all()
    serializer_class = AddToCartSerializer
    permission_classes = [IsAuthenticated, ]


    def destroy(self, request, pk):
        if cart_helper.delete_from_cart(request, pk):
            return Response({"data": {"message": "Successfully removed from wishlist"}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": False, "data": {"message": "Could not delete product from wishlist."}},
                            status=status.HTTP_400_BAD_REQUEST)
'''


"""class CartItemAPIView(ListCreateAPIView):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated,]
    def get_queryset(self):
        user = self.request.user.id
        queryset = AddToCart.objects.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        # cart = get_object_or_404(AddToCart, user=user)
        product = get_object_or_404(Product, pk=request.data["product"])
        current_item = AddToCart.objects.filter(user=user, product=product)

        '''if user == product.user:
            raise PermissionDenied("This Is Your Product")'''

        if current_item.count() > 0:
            raise NotAcceptable("You already have this item in your shopping cart")

        try:
            quantity = int(request.data["quantity"])
        except Exception as e:
            raise ValidationError("Please Enter Your Quantity")

        if quantity > AddToCart.quantity:
            raise NotAcceptable("You order quantity more than the seller have")

        cart_item = AddToCart(user=user, product=product, quantity=quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        total = float(product.price) * float(quantity)
        #cart.total = total
        # cart.save()
        '''push_notifications(
            cart.user,
            "New cart product",
            "you added a product to your cart " + product.title,
        )'''

        return Response(serializer.data,
                        product.name + {"data": {"message": "Successfully added in cart "}},
                        status=status.HTTP_201_CREATED
        )
"""