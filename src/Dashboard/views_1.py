from django.shortcuts import render
from django.db.models import Q, Count, Sum
from CartSystem.models import AddToCart, WishList
from products.models import Product
from products.serializers import ProductSerializer
from orders.models import OrderDetail, OrderProductDetail, ContactAddress
from Dashboard.serializers import PopularProductSerializer, FreshArrivalsProductSerializers
from common.models import User
from vendor.models import Vendor, VendorAddress
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.serializers import ContactAddressSerializer
from vendor.serializers import VendorProfileAddressSerializer
import geopy.distance
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

class PopularProductInWishListAPIView(APIView):

    def get(self, request):
        wishlistProduct = WishList.objects.values('product__name', 'product__short_description').annotate(
            total=Count('product')).order_by('product')[:10]
        return Response(
            {
                "status": "Success",
                "wishlistData": wishlistProduct,
            },
            status=status.HTTP_200_OK
        )

class PopularProductInCartAPIView(APIView):

    def get(self, request):
        cartProduct = AddToCart.objects.values('product__name', 'product__short_description').annotate(
            total=Count('product')).order_by('product')[:10]
        return Response(
            {
                "status": "Success",
                "cartData": cartProduct,
            },
            status=status.HTTP_200_OK
        )

class PopularOrderedProductWitoutLocationAPIView(APIView):

    def get(self, request):
        if self.request.user.id:
            userObj = User.objects.get(id=self.request.user.id)

            # Get UserAddress Object
            userAddressObj = ContactAddress.objects.get(user=userObj, is_default=True)
            user_pin_code = userAddressObj.postcode

            # get Useraddress serialized data
            userAddressSerializerObj = ContactAddressSerializer(userAddressObj, many=False)
            userAddress = userAddressSerializerObj.data

            # we get user coordinates using user latitude, longitude
            userAddressCords = (userAddress["map_lat"], userAddress["map_lng"])

            try:
                orderedProduct = OrderProductDetail.objects.values('product').annotate(
                    total=Count('product')).order_by('product')[:10]

                allPopularProduct = []
                for pProduct in orderedProduct:

                    onePopularProduct = Product.objects.filter(id=pProduct["product"])
                    popularProductData = ProductSerializer(onePopularProduct, many=True).data

                    productList = []
                    for onePopularProductdata in popularProductData:
                        # # get Vendor Object
                        vendorObj = Vendor.objects.get(id=onePopularProductdata["vendor"])
                        print(vendorObj)

                        # get Vendor Address Object and vendorAddress serialzized data
                        vendorAddressObj = VendorAddress.objects.get(vendor=vendorObj)
                        vendorAddressSerializerObj = VendorProfileAddressSerializer(vendorAddressObj, many=False)
                        vendorAddress = vendorAddressSerializerObj.data

                        # we get vendor coordinates using vendor latitude and longitude
                        vendorAddressCords = (vendorAddress["map_lat"], vendorAddress["map_lng"])
                        try:
                            vendor_pin_codes = [pin_code.strip() for pin_code in
                                                vendorObj.delivering_pincodes.split(",")]
                        except:
                            vendor_pin_codes = []
                        # 12.9045916   #77.55211

                        # calculate distance in kilometer by iser and vendor coordinate
                        distanceBetweenVendorAndUser = geopy.distance.geodesic(userAddressCords, vendorAddressCords).km
                        print(distanceBetweenVendorAndUser)
                        if user_pin_code in vendor_pin_codes:
                            # onePopularProduct = Product.objects.filter(id=pProduct["product"])
                            # print(onePopularProduct)
                            onePopularProductdata["vendorDistance"] = distanceBetweenVendorAndUser
                            allPopularProduct.append(onePopularProductdata)
                            # allPopularProduct.append((ProductSerializer(onePopularProduct, many=True).data))

                return Response(
                    {
                        "status": "Success",
                        "count": len(allPopularProduct),
                        "data": allPopularProduct,
                    },
                    status=status.HTTP_200_OK,
                )
            except OrderProductDetail.DoesNotExist:
                return Response({"status": "warning", "message": "Opps! Popular Product not found!!!", "data": [],
                                 }, status=204,
                                )
        else:

            try:
                orderedProduct = OrderProductDetail.objects.values('product').annotate(
                    total=Count('product')).order_by('product')[:10]

                allPopularProduct = []
                for pProduct in orderedProduct:
                    onePopularProduct = Product.objects.filter(id=pProduct["product"])
                    #print(onePopularProduct)
                    allPopularProduct.append(ProductSerializer(onePopularProduct, many=True).data)

                return Response(
                    {
                        "status": "Success",
                        "data": allPopularProduct,
                    },
                    status=status.HTTP_200_OK,
                )
            except OrderProductDetail.DoesNotExist:
                return Response({"status": "warning","message": "Opps! Popular Product not found!!!","data": [],
                    }, status=204,
                )


# Popular Product By Location
class PopularOrderedProductAPIView(APIView):

    # permission_classes = [IsAuthenticated]
    def get(self, request):

        # Get User Object
        userObj = User.objects.get(id=self.request.user.id)

        # Get UserAddress Object
        userAddressObj = ContactAddress.objects.get(user=userObj, is_default=True)
        user_pin_code = userAddressObj.postcode


        # get Useraddress serialized data
        userAddressSerializerObj = ContactAddressSerializer(userAddressObj, many=False)
        userAddress = userAddressSerializerObj.data

        # we get user coordinates using user latitude, longitude 
        userAddressCords = (userAddress["map_lat"], userAddress["map_lng"])

        try:
            orderedProduct = OrderProductDetail.objects.values('product').annotate(
                total=Count('product')).order_by('product')[:10]

            allPopularProduct = []
            for pProduct in orderedProduct:
                
                onePopularProduct = Product.objects.filter(id=pProduct["product"])
                popularProductData = ProductSerializer(onePopularProduct, many=True).data
                
                productList = []
                for onePopularProductdata in popularProductData:
                    # # get Vendor Object
                    vendorObj = Vendor.objects.get(id = onePopularProductdata["vendor"])
                    print(vendorObj)
                
                    # get Vendor Address Object and vendorAddress serialzized data
                    vendorAddressObj = VendorAddress.objects.get(vendor=vendorObj)
                    vendorAddressSerializerObj = VendorProfileAddressSerializer(vendorAddressObj, many=False)
                    vendorAddress = vendorAddressSerializerObj.data

                    # we get vendor coordinates using vendor latitude and longitude
                    vendorAddressCords = (vendorAddress["map_lat"], vendorAddress["map_lng"])
                    try:
                        vendor_pin_codes = [pin_code.strip() for pin_code in vendorObj.delivering_pincodes.split(",")]
                    except:
                        vendor_pin_codes = []
                    #12.9045916   #77.55211

                    # calculate distance in kilometer by iser and vendor coordinate
                    distanceBetweenVendorAndUser = geopy.distance.geodesic(userAddressCords, vendorAddressCords).km
                    print(distanceBetweenVendorAndUser)
                    if user_pin_code in vendor_pin_codes:
                        # onePopularProduct = Product.objects.filter(id=pProduct["product"])
                        # print(onePopularProduct)
                        onePopularProductdata["vendorDistance"] = distanceBetweenVendorAndUser
                        allPopularProduct.append(onePopularProductdata)
                        # allPopularProduct.append((ProductSerializer(onePopularProduct, many=True).data))


            return Response(
                {
                    "status": "Success",
                    "count": len(allPopularProduct),
                    "data": allPopularProduct,
                },
                status=status.HTTP_200_OK,
            )
        except OrderProductDetail.DoesNotExist:
            return Response({"status": "warning","message": "Opps! Popular Product not found!!!", "data": [],
                }, status=204,
            )


# Fresh Arriavals Product with Location
class FreshArrivalProductWithLocationAPIView(APIView):

    # permission_classes = [IsAuthenticated]
    def get(self, request):

        if self.request.user.id:

            # Get User Object
            userObj = User.objects.get(id=self.request.user.id)
            print("userobj", userObj)

            # Get UserAddress Object
            userAddressObj = ContactAddress.objects.get(user=userObj, is_default=True)

            # get Useraddress serialized data
            userAddressSerializerObj = ContactAddressSerializer(userAddressObj, many=False)
            userAddress = userAddressSerializerObj.data
            user_pin_code = userAddressObj.postcode
            print("user_pincode", user_pin_code)

            # we get user coordinates using user latitude, longitude
            userAddressCords = (userAddress["map_lat"], userAddress["map_lng"])
            try:
                newArrivalProduct = Product.objects.order_by('-created_at')[:20]
                # newArrivalProductSerializerData = FreshArrivalsProductSerializers(newArrivalProduct, many=True).data
                newArrivalProductSerializerData = ProductSerializer(newArrivalProduct, many=True).data
                productList = []
                for oneFreshArrival in newArrivalProductSerializerData:
                    print(oneFreshArrival)
                    # get Vendor Object
                    vendorObj = Vendor.objects.get(id = oneFreshArrival["vendor"])
                    print("vendor pincode", vendorObj.delivering_pincodes.split(","))
                    print(vendorObj)
                    try:
                        vendor_pin_codes = [pin_code.strip() for pin_code in vendorObj.delivering_pincodes.split(",")]
                    except:
                        vendor_pin_codes = []

                    # get Vendor Address Object and vendorAddress serialzized data
                    vendorAddressObj = VendorAddress.objects.get(vendor=vendorObj)
                    vendorAddressSerializerObj = VendorProfileAddressSerializer(vendorAddressObj, many=False)
                    vendorAddress = vendorAddressSerializerObj.data

                    # we get vendor coordinates using vendor latitude and longitude
                    vendorAddressCords = (vendorAddress["map_lat"], vendorAddress["map_lng"])        #12.9045916   #77.55211
                    # print(vendorAddressCords)
                    # calculate distance in kilometer by iser and vendor coordinate
                    distanceBetweenVendorAndUser = geopy.distance.geodesic(userAddressCords, vendorAddressCords).km
                    print(distanceBetweenVendorAndUser)

                    if user_pin_code in vendor_pin_codes:

                        # onePopularProduct = Product.objects.filter(id=pProduct["product"])
                        # print(onePopularProduct)
                        oneFreshArrival["vendorDistance"] = distanceBetweenVendorAndUser
                        productList.append(oneFreshArrival)
                        # print(newArrivalProductSerializerData)
                return Response(
                    {
                        "status": "Success",
                        "count": len(productList),
                        "data": productList,
                    },
                    status=status.HTTP_200_OK,
                )
            except OrderProductDetail.DoesNotExist:
                return Response({"status": "warning", "message": "Opps! Fresh Arrival Product not found!!!","data": [],
                    },status=204,
                )
        else:
            try:
                print("Hi")
                newArrivalProduct = Product.objects.order_by('-created_at')[:20]
                newArrivalProductSerializerData = FreshArrivalsProductSerializers(newArrivalProduct, many=True).data
                print(newArrivalProduct)
                return Response(
                    {
                        "status": "Success",
                        "count": len(newArrivalProductSerializerData),
                        "data": newArrivalProductSerializerData,
                    },
                    status=status.HTTP_200_OK,
                )
            except OrderProductDetail.DoesNotExist:
                return Response({"status": "warning", "message": "Opps! Fresh Arrival Product not found!!!", "data": [],
                                 }, status=204,
                                )



# Fresh Arrival Product without location
class FreshArrivalProductAPIView(APIView):

    def get(self, request):
        try:
            newArrivalProduct = Product.objects.order_by('-created_at')[:20]
            newArrivalProductSerializerData = FreshArrivalsProductSerializers(newArrivalProduct, many=True).data
            print(newArrivalProduct)
            return Response(
                {
                    "status": "Success",
                    "count": len(newArrivalProductSerializerData),
                    "data": newArrivalProductSerializerData,
                },
                status=status.HTTP_200_OK,
            )
        except OrderProductDetail.DoesNotExist:
            return Response({"status": "warning", "message": "Opps! Fresh Arrival Product not found!!!","data": [],
                },status=204,
            )


# class FrequentlyOrderedProductAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = self.request.user.id
#         try:
#             orderedProduct = OrderProductDetail.objects.values('product', user).annotate(
#                 total=Count('product')).order_by('product')[:10]
#
#             allPopularProduct = []
#             for pProduct in orderedProduct:
#                 onePopularProduct = Product.objects.filter(id=pProduct["product"])
#                 #print(onePopularProduct)
#                 allPopularProduct.append(ProductSerializer(onePopularProduct, many=True).data)
#
#             return Response(
#                 {
#                     "status": "Success",
#                     "data": allPopularProduct,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         except OrderProductDetail.DoesNotExist:
#             return Response({"status": "warning","message": "Opps! Popular Product not found!!!","data": [],
#                 }, status=204,
#             )
