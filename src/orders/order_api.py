from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import OrderDetailSerializer, OrderProductDetailSerializer, ContactAddressSerializer
from .models import OrderDetail, OrderProductDetail, ContactAddress
from CartSystem.models import AddToCart
from CartSystem.serializers import AddToCartSerializer, CartItemSerializer
from Offers.serializers import OfferSerializer, OfferSerializerInPutValidatation
from Offers.models import Offer
from Offers import helper
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
import decimal
from products.models import Product


# OrderDetail API

class OrderWithOfferAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = self.request.user

        # Shipping(Customer-Address) Address Data
        user_address = ContactAddress.objects.filter(user=user, is_default=True).first()
        user_address_serializer_data = ContactAddressSerializer(user_address).data

        # Cart Data
        cart = AddToCart.objects.filter(user=user)
        cart_serializer_data = CartItemSerializer(cart, many=True).data

        # Offer-Discount Data
        offer = helper.getOfferDiscountAmnt(request)
        data = offer[0]
        print(data)

        return Response(
            {
                "status":"success",
                "responseData" : {"discount": data}

        })





