from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, mixins, status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from products.models import Product
from common.models import User
from products.serializers import ProductSerializer
from CartSystem.common import cart_system as cart_helper
from CartSystem.serializers import WishlistProductSerializer, WishlistSerializer, AddToCartSerializer, AddToWishlistSerializer
from CartSystem.models import AddToCart, WishList as WishlistModel
from rest_framework.views import APIView

# WishList Api for Product Add/get to Wishlist
class WishList(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = WishlistModel.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated, ]
    # print(queryset)
    def list(self, request, *args, **kwargs):
        wishlist = cart_helper.get_wishlist_by_user(request)
        print(wishlist)
        return Response({"status": True, "data": wishlist}, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            product = Product.objects.get(
                id=request.data['product'])     # id=request.data['productId']
        except (Exception, Product.DoesNotExist) as e:
            return Response({"data": {"message": "Product does not exists."}}, status=status.HTTP_404_NOT_FOUND)
        if not cart_helper.check_whislist(request, product):
            wishlist = WishlistModel.objects.create(
                user=request.user, product=product)
            return Response({"data": {"message": "Product added to wishlist"}}, status=status.HTTP_201_CREATED)
        else:
            return Response({"data": {"message": "Product is already added to wishlist."}},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

class WishlistAdd(CreateAPIView):

    queryset = WishlistModel.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated,]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        print(user)
        try:
            product = Product.objects.get(
                id=request.data['product'])
            print(product)
        except (Exception, Product.DoesNotExist) as e:
            return Response({"data": {"message": "Product does not exists."}}, status=status.HTTP_404_NOT_FOUND)
        if not cart_helper.check_whislist(request, product):
            wishlist = WishlistModel.objects.create(
                user=user, product=product)
            print(wishlist)
            return Response({"data": {"message": "Product added to wishlist"}}, status=status.HTTP_200_OK)
        else:
            return Response({"data": {"message": "Product is already added to wishlist."}},
                            status=status.HTTP_406_NOT_ACCEPTABLE)


# Delete wishlist Product
class WishlistDestoryApi(DestroyAPIView):

    queryset = WishlistModel.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated, ]

    def destroy(self, request, pk):
        if cart_helper.delete_from_wishlist(request, pk):
            return Response({"data": {"message": "Successfully removed from wishlist"}}, status=status.HTTP_200_OK)
        else:
            return Response({"status": False, "data": {"message": "Could not delete product from wishlist."}},
                            status=status.HTTP_400_BAD_REQUEST)


'''class WishlistAll(ListAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = WishlistModel.objects.all()
    serializer_class = WishlistSerializer

    # print(queryset)
'''

'''class WishListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    model = WishlistModel
    # queryset = WishList.objects.all().count()
    serializer_class = WishlistSerializer

    def get_queryset(self, *args, **kwargs):
        return WishlistModel.objects.filter(user=self.request.user.id)
'''

# Add Product to Wishlist
'''class AddWishListApi(APIView):

    def post(self, request, *args, **kwargs):
        product = request.data.get('product', False)
        user = self.request.user.id
        data = {}
        checkw = WishlistModel.objects.filter(product=product, user=user)
        if checkw > 0:
            data={
                'bool':False,
                'message': 'No Products in Wishlist'
            }
        else:
            wishlist = WishlistModel.objects.create(
                product=product,
                user=user
            )
            print(wishlist)
            data = {
                'bool': True,
                'message' : 'Product is Added in Wishlist',
            }

        return Response(data, status=status.HTTP_200_OK)
'''

'''class WishListAddApi(CreateAPIView):

    # permission_classes = [IsAuthenticated, ]
    queryset = WishlistModel.objects.all()
    # serializer_class = AddToWishlistSerializer
    serializer_class = WishlistSerializer
'''

class WishlistToCart(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = WishlistModel.objects.none()
    serializer_class = WishlistProductSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        '''if not request.data['wishlist']:
            return Response({"status": False, "data": {"msg": "Data is missing. Please try again."}},
                            status=status.HTTP_400_BAD_REQUEST)'''

        try:
            wishlist = WishlistModel.objects.get(
                id=request.data['wishlist'])
            new_cart = AddToCart.objects.get_or_create(
                user=request.user, product=wishlist.product)
            if new_cart:
                if not wishlist.delete():
                    new_cart.delete()
                    return Response({"status": False, "data": {"msg": "Something went wrong. Please try again."}},
                                    status=status.HTTP_409_CONFLICT)
            else:
                return Response({"status": False, "data": {"msg": "Something went wrong. Please try again."}},
                                status=status.HTTP_409_CONFLICT)
            return Response({"status": True, "data": {"msg": "Successfully added to cart."}},
                            status=status.HTTP_200_OK)
        except (Exception, WishlistModel.DoesNotExist):
            return Response({"status": False, "data": {"msg": "Data not found."}},
                            status=status.HTTP_404_NOT_FOUND)


class WishListToCart(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = WishlistModel.objects.none()
    serializer_class = WishlistProductSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request):

        if not request.data["quantity"]:
            return Response({"status": False, "data": {"msg": "Data is missing. Please try again."}}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wishlist = WishlistModel.objects.get(
                id=request.data['wishlist']) # id=request.data['wishlist']
            new_cart = AddToCart.objects.get_or_create(
                user=User.objects.get(id=self.request.user.id), product=wishlist.product, quantity=request.data["quantity"])
            if new_cart:
                if not wishlist.delete():
                    new_cart.delete()
                    return Response({"status": False, "data": {"msg": "Something went wrong. Please try again."}}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({"status": False, "data": {"msg": "Something went wrong. Please try again."}}, status=status.HTTP_409_CONFLICT)
            return Response({"status": True, "data": {"msg": "Successfully added to cart."}}, status=status.HTTP_200_OK)
        except (Exception, WishlistModel.DoesNotExist):
            return Response({"status": False, "data": {"msg": "Data not found."}}, status=status.HTTP_404_NOT_FOUND)

