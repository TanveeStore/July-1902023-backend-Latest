from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import OfferSerializer, OfferSerializerInPutValidatation
from .models import Offer
from CartSystem.models import AddToCart
from CartSystem.serializers import AddToCartSerializer
from CartSystem.common import cart_system
from Offers import helper
from rest_framework.views import APIView
from rest_framework.generics import DestroyAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
from datetime import datetime, timedelta
import time
from django.utils import timezone
import decimal





# API View for Offer
class OfferApiView(APIView):
    # permission_classes = [IsAuthenticated,]
    def get(self, request):
        offer_serializer = Offer.objects.all().order_by('-id')
        serializer = OfferSerializer(offer_serializer, many=True)
        return Response({'count' : len(serializer.data) , 'data':serializer.data})

    # def post(self, request, *args, **kwargs):
    #
    #     serializer = OfferSerializer(data=request.data, context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(
    #             {
    #                 "errors":False,
    #                 "data":serializer.data},
    #             status=status.HTTP_201_CREATED
    #         )
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfferCouponApiView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()


class ApplyOfferCouponAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        helperResopnse, responseCode = helper.getOfferDiscountAmnt(request)
        if helperResopnse["status"]=="success":
            return Response({"status": helperResopnse["status"], "message": helperResopnse["message"],"discount":helperResopnse["discount"]},
                            status=responseCode)
        else:
            return Response({"status":helperResopnse["status"],"message":helperResopnse["message"]},status=responseCode)