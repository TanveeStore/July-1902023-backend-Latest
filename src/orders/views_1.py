from operator import le
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    OrderDetailSerializer, OrderProductDetailSerializer,
    ContactAddressSerializer, VendorOrderDetailsSerializer, OrderProductDetailSerializerD2, ReturnProductSerializer,
    OrderDetailSerializers2)

from .models import OrderDetail, OrderProductDetail, ContactAddress, VendorOrderDetails, ReturnProduct
from CartSystem.models import AddToCart
from CartSystem.serializers import AddToCartSerializer, CartItemSerializer
from Offers.serializers import OfferSerializer, OfferSerializerInPutValidatation
from Offers.models import Offer
from Offers import helper
from rest_framework.views import APIView
from vendor.models import Vendor
from rest_framework.generics import DestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status
import decimal
from products.models import Product, ProductWeight
from products.serializers import ProductWeightSerializer
from CartSystem.common.cart_system import get_cart_amt_detail, deleteCartAllProducts
import razorpay
from django.conf import settings
from common.utils import CommonUtils
from common.models import User
from Notifications.models import Notifications
from deliveryCharge.models import DeliveryCharge
from deliveryCharge.serializers import DeliveryChargeSerializer

# client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))
# client.order.payment(orderId)

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))


class orderHelperClass():
    def createOrder(self, request):
        user = request.user
        userObj = User.objects.get(id=request.user.id)
        payment_method = request.data.get("payment_method", False)
        if payment_method != "COD" and payment_method != "Razorpay" and payment_method != "wallet":
            return {
                "status": "warning",
                "status_code": 400,
                "message": "Invalid payment method"
            }

        cartAmtDetails = get_cart_amt_detail(request)
        # print("Total Cart quantity :", cartAmtDetails["totalCartProductQty"])
        totalQuantity = cartAmtDetails["totalCartProductQty"]

        if cartAmtDetails["cartNoOfProducts"] < 1:
            return {
                "status": "warning",
                "status_code": 406,
                "message": "Opps!! You don't have any products in cart to place order!"
            }

        # Discount 0ffer
        totalDiscount = 0
        offerCode = request.data.get("offer_code", False)
        discountResponse, discountStatus = helper.getOfferDiscountAmnt(request)
        if discountStatus == 200:
            totalDiscount = discountResponse["discount"]

        # Delivery Charge
        # totalShippingCharge = 0.00 if cartAmtDetails["cartAmt"] >= 500 else 10.0
        deliveryChargeObject = DeliveryCharge.objects.filter(status="active")
        deliveryChargeData = DeliveryChargeSerializer(deliveryChargeObject, many=True).data
        for oneDeliveryRate in deliveryChargeData:
            oneDeliveryCharge = oneDeliveryRate["deliveryPrice"]
            oneDeliveryMinCharge = oneDeliveryRate["min_order_amt"]
            oneDeliveryMaxCharge = oneDeliveryRate["max_order_amt"]

        totalShippingCharge = decimal.Decimal(oneDeliveryCharge) if decimal.Decimal(
            cartAmtDetails["cartAmt"]) >= decimal.Decimal(oneDeliveryMinCharge) and decimal.Decimal(
            cartAmtDetails["cartAmt"]) <= decimal.Decimal(oneDeliveryMaxCharge) else decimal.Decimal(0.0)

        grandTotal = (cartAmtDetails["cartAmt"] + cartAmtDetails["cartTaxAmt"] + decimal.Decimal(
            totalShippingCharge)) - decimal.Decimal(totalDiscount)
        grandSubTotal = grandTotal + decimal.Decimal(totalDiscount)

        # Shipping(Customer-Address) Address Data
        user_address = ContactAddress.objects.filter(
            user=user, is_default=True).first()
        user_address_serializer_data = ContactAddressSerializer(
            user_address).data

        # Cart Data
        cart = AddToCart.objects.filter(user=user)
        cart_serializer_data = CartItemSerializer(cart, many=True).data

        order_status = "Pending"

        # Creating Order
        order = OrderDetail.objects.create(user=user,
                                           address=user_address,
                                           offer_code=offerCode,
                                           price=cartAmtDetails["cartAmt"],
                                           shipping_charge=totalShippingCharge,
                                           tax=cartAmtDetails["cartTaxAmt"],
                                           offer_discount=totalDiscount,
                                           totalOrderdQty=totalQuantity,
                                           grand_total=grandTotal,
                                           payment_method=payment_method,
                                           payment_status="Pending",
                                           order_status=order_status)
        order.save()
        orderCartItemSavedCounter = 0

        for oneCartItem in cart_serializer_data:
            product_weight_obj = ProductWeight.objects.get(id=oneCartItem['product_weight'])
            # product_weight_serializer = CartItemSerializer(product_weight_obj, many=True)
            orderItemsCreate = OrderProductDetail.objects.create(order=order,
                                                                 product=Product.objects.get(
                                                                     id=oneCartItem["product"]["id"]),
                                                                 quantity=oneCartItem["quantity"],
                                                                 product_weight = product_weight_obj
                                                                 #  userOrderedProductStatus=order.order_status,
                                                                 )
            orderItemsCreate.save()
            orderCartItemSavedCounter += 1

            vendorObj = Vendor.objects.get(id=oneCartItem["product"]["vendor"])

            cartItemPrice = float(oneCartItem["product"]["price"])
            cartItemQuantity = int(oneCartItem["quantity"])
            cartItemTaxPercentage = float(oneCartItem["product"]["tax"])
            cartItemTotalTaxAmt = float(
                ((cartItemPrice * cartItemQuantity) * cartItemTaxPercentage) / 100)
            cartItemTotalPrice = float(cartItemPrice * cartItemQuantity)
            cartItemGrandTotalPrice = float(
                cartItemTotalPrice + cartItemTotalTaxAmt)

            try:
                vendorOrderObj = VendorOrderDetails.objects.get(
                    order=order, vendor=vendorObj)
                vendorOrderData = VendorOrderDetailsSerializer(
                    vendorOrderObj, many=False).data

                vendorOrderUpdateData = {
                    "total_items": 1 + vendorOrderData["total_items"],
                    "total_quantity": cartItemQuantity + vendorOrderData["total_quantity"],
                    "total_price": cartItemTotalPrice + float(vendorOrderData["total_price"]),
                    "total_tax": cartItemTotalTaxAmt + float(vendorOrderData["total_tax"]),
                    "grand_total": cartItemGrandTotalPrice + float(vendorOrderData["grand_total"])
                }
                VendorOrderDetailsSerializerObj = VendorOrderDetailsSerializer(vendorOrderObj, vendorOrderUpdateData,
                                                                               partial=True)
                if VendorOrderDetailsSerializerObj.is_valid():
                    VendorOrderDetailsSerializerObj.save()

            except VendorOrderDetails.DoesNotExist:
                # if order_status == "Order Placed":
                VendorOrderDetailsObj = VendorOrderDetails.objects.create(vendor=vendorObj,
                                                                          order=order,
                                                                          total_items=1,
                                                                          total_quantity=cartItemQuantity,
                                                                          total_price=cartItemTotalPrice,
                                                                          total_tax=cartItemTotalTaxAmt,
                                                                          grand_total=cartItemGrandTotalPrice)
                VendorOrderDetailsObj.save()

        if len(cart_serializer_data) == orderCartItemSavedCounter:
            isDeletedCartAllItems = deleteCartAllProducts(request)

            for oneCartItem in cart_serializer_data:
                try:
                    productweightObj = ProductWeight.objects.get(id=oneCartItem['product_weight'])
                    productweightObj.qty = int(productweightObj.qty) - int(oneCartItem["quantity"])
                    print(productweightObj.qty, oneCartItem['quantity'])
                    productweightObj.save()
                except Product.DoesNotExist:
                    pass
            # if order_status = "Order Placed":
            if payment_method == "COD":
                # Customer Order Sms
                textMessage = f'Hello {userObj.first_name}, Your order {order.order_number} has been received. Please have patience, your order will be delivered with in 8 business hours. see you soon , Team Tanvee Store'
                orderResponse = CommonUtils.SendMobileMessage([userObj.mobile], "order-placed", textMessage)

                # # Customer OrderStatus Notification
                # userNotificationObj = Notifications.objects.create(user=userObj,
                #                                             notificationText=textMessage,
                #                                             notificationType ="order",
                #                                             seenStatus=False)
                # userNotificationObj.save()
                # CommonUtils.sendPushNotification(userType="customer", fcmTokens=[userObj.fcm_token], title="Tanvee Notification", msg=textMessage, image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb", dataObject=None)

                # # Vendor Order Notification
                # vendorNotificationMessage = f'Hello {vendorObj.org_name}, The Product order #{order.order_number} has been received. The Product {productObj.name} is Order by Customer. And The Status of That Product is {order.order_status}. Team Tanvee Store'
                # notificationVendorObj = Notifications.objects.create(user=vendorObj.user,
                #                                             notificationText=vendorNotificationMessage,
                #                                             notificationType ="order",
                #                                             seenStatus=False)
                # notificationVendorObj.save()

                # CommonUtils.sendPushNotification(userType="vendor", fcmTokens=[vendorObj.user.fcm_token], title="Tanvee Notification", msg=vendorNotificationMessage, image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb", dataObject=None)

            return {
                "status": "success",
                "status_code": 200,
                "message": "Thanks!! Your order is successfully placed!",
                "data": {
                    "order_id": order.order_number,
                    "total_amount": cartAmtDetails["cartAmt"],
                    "total_tax": cartAmtDetails["cartTaxAmt"],
                    "total_shipping": totalShippingCharge,
                    "sub_total": grandSubTotal,
                    "total_discount": totalDiscount,
                    "grand_total": grandTotal
                }
            }
        else:
            return {
                "status": "warning",
                "status_code": 400,
                "message": "Opps!! Something went wrong, try to re-order!"
            }


# OrderDetail API
class OrderDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        orderList = OrderDetail.objects.filter(user=user)
        orderListSerializeData = OrderDetailSerializer(
            orderList, many=True).data

        if len(orderListSerializeData) > 0:
            responseData = {
                "status": "success",
                "message": "Order list found",
                "data": orderListSerializeData
            }
            return Response(responseData, status=status.HTTP_200_OK)
        else:
            responseData = {
                "status": "warning",
                "message": "You don't have any order!",
                "data": []
            }
            return Response(responseData, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        user = request.user
        payment_method = self.request.data.get("payment_method", False)

        userObj = User.objects.get(id=request.user.id)

        if payment_method != 'COD':
            return Response({"status": "warning", "message": "Please select COD for place order by this api"},
                            status=406)

        if payment_method == 'COD':
            orderHelperClassObj = orderHelperClass()
            createOrderHelperResponse = orderHelperClassObj.createOrder(request)

            orderDetails = createOrderHelperResponse["data"]
            # currency = "INR"
            # amount = float(orderDetails["grand_total"])
            order_number = orderDetails["order_id"]

            if createOrderHelperResponse["status"] == "success":
                orderObj = OrderDetail.objects.get(order_number=order_number, user=userObj)
                orderDetailsData = OrderDetailSerializer(orderObj, many=False).data

                # orderObj.payment_status = "Paid"
                orderObj.order_status = "Order Placed"
                orderObj.save()
                return Response(createOrderHelperResponse, status=200)
            else:
                return Response(createOrderHelperResponse, status=createOrderHelperResponse["status_code"])


class CreateRazorpayOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        payment_method = self.request.data.get("payment_method", False)

        if payment_method != 'Razorpay':
            return Response({"status": "warning", "message": "Please select Razorpay to place order by this api"},
                            status=406)

        orderHelperClassObj = orderHelperClass()
        createOrderHelperResponse = orderHelperClassObj.createOrder(request)
        if createOrderHelperResponse["status"] == "success":
            orderDetails = createOrderHelperResponse["data"]

            currency = "INR"
            amount = int(float(orderDetails["grand_total"]))

            order_number = orderDetails["order_id"]

            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create(dict(amount=amount * 100,
                                                               currency=currency,
                                                               payment_capture="1",
                                                               receipt=order_number))

            responseData = {
                "status": "success",
                "message": "Waiting for razorpay payment",
                "data": razorpay_order,
                "OrderAmount": amount,
                "OrderPaymentId": razorpay_order["id"]
            }
            return Response(responseData, status=status.HTTP_200_OK)
        else:
            responseData = {
                "status": "warning",
                "message": "Opps!! Something went wrong, try again!!!"
            }
            return Response(createOrderHelperResponse, status=createOrderHelperResponse["status_code"])


# [POST] api/customer/order-place-razorpay-verify/
# [REQUEST]:
# {
#     "order_number" : "ORD50807130303",
#     "razorpay_order_id":"",
#     "razorpay_payment_id": "",
#     "razorpay_signature": ""
# }
# [RESPONSE]:
# {
#     "order_number" : "ORD50807130303",
#     "razorpay_order_id":"",
#     "razorpay_payment_id": "",
#     "razorpay_signature": ""
# }
class RazorPayVerifyPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        userObj = self.request.user

        # order_number is nothing but a receipt no which is provided by create order api response
        order_number = request.data.get("order_number", False)
        razorpay_payment_id = request.data.get('razorpay_payment_id', '')
        razorpay_order_id = request.data.get('razorpay_order_id', '')
        razorpay_signature = request.data.get('razorpay_signature', '')

        try:
            orderObj = OrderDetail.objects.get(
                order_number=order_number, user=userObj)
            orderDetailsData = OrderDetailSerializer(orderObj, many=False).data

            currency = 'INR'
            amount = int(float(orderDetailsData["grand_total"]) * 100)  # Rs.

            try:

                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                }

                # verify the payment signature.
                result = razorpay_client.utility.verify_payment_signature(params_dict)

                orderObj.payment_status = "Paid"
                orderObj.order_status = "Order Placed"
                orderObj.save()

                if orderObj.payment_status == "Paid":
                    # Customer Order Sms
                    textMessage = f'Hello {userObj.first_name}, Your order {orderObj.order_number} has been received. Please have patience, your order will be delivered with in 8 business hours. see you soon , Team Tanvee Store'
                    orderResponse = CommonUtils.SendMobileMessage([userObj.mobile], "order-placed", textMessage)

                    # Customer OrderStatus Notification
                    userNotificationObj = Notifications.objects.create(user=userObj,
                                                                       notificationText=textMessage,
                                                                       notificationType="order",
                                                                       seenStatus=False)
                    userNotificationObj.save()
                    CommonUtils.sendPushNotification(userType="customer", fcmTokens=[userObj.fcm_token],
                                                     title="Tanvee Notification", msg=textMessage,
                                                     image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb",
                                                     dataObject=None)

                return Response({"status": "success", "message": "Payment Success!"}, status=200)
                # if result is not None:

                #     # if signature verification fails.
                #     return Response({"status": "warning", "message": "Invalid Payment!", "Others": params_dict}, status=200)

                # else:
                #     # capture the payment
                #     # razorpay_client.payment.capture(razorpay_payment_id, amount, currency)
                #     # render success page on successful caputre of payment
                #     return Response({"status": "success", "message": "Payment Success!"}, status=200)

            except:
                # if we don't find the required parameters in POST data
                return Response({"status": "warning", "message": "Invalid Inputes!"},
                                status=status.HTTP_400_BAD_REQUEST)

        except OrderDetail.DoesNotExist:
            return Response({
                "status": "warning",
                "message": "Order id not valid"
            }, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailUpdateApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def patch(self, request, pk):
        user_id = self.request.user.id
        try:
            user = request.user
            order = OrderDetail.objects.get(pk=pk)
            order_status = request.data['order_status']
            # order_status =order_status
            serializer = OrderDetailSerializer(
                order, order_status=order_status, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            responseData = {
                "status": "success",
                "orderNumber": order.order_number,
                "order_status": order_status,
                "msg": "Order Cancelled.",
                "data": serializer.data
            }

            return Response(responseData, status=status.HTTP_200_OK)

        except (OrderDetail.DoesNotExist, Exception) as e:
            return Response({"data": {"message": "Somthing Went to Wrong!!"}}, status=status.HTTP_404_NOT_FOUND)

    # def put(self, request, pk):
    #     user = request.user
    #     user_address = get_object_or_404(ContactAddress, pk=pk)
    #     if user_address.user != user:
    #         raise PermissionDenied("This Action You can't Perform!!")
    #     serializer = ContactAddressSerializer(
    #     user_address, data=request.data, context={"request": request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     responseData = {
    #         "status": "success",
    #         "message": "Your Address is Successfully Updated!!",
    #         "data": serializer.data
    #         }
    #
    #     return Response(responseData, status = status.HTTP_201_CREATED)


# OrderDetail API

# class OrderProductsHistoryAPIView(APIView):
#     permission_classes = [IsAuthenticated, ]
#
#     def get(self,request):
#         user = request.user
#         order_number = request.data.get('order_number')
#         order = OrderDetail.objects.filter(order_number=order_number)
#         orderedproductList = OrderProductDetail.objects.filter(order=order)
#         orderedProductListSerializeData = OrderProductDetailSerializer(orderedproductList, many=True).data
#
#         #print(orderListSerializeData)
#         if len(orderedProductListSerializeData)>0:
#             responseData = {
#                 "status": "success",
#                 "message": "Ordered Product list found!!!",
#                 "data": orderedProductListSerializeData
#             }
#             return Response(responseData, status=status.HTTP_200_OK)
#         else:
#             responseData = {
#                 "status": "warning",
#                 "message": "No order Placed!"
#             }
#             return Response(responseData, status=status.HTTP_404_NOT_FOUND)


# Ordered Product History
class OrderProductsHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderProductDetailSerializer
    queryset = OrderProductDetail.objects.all().order_by('-id')


class UserOrderProductHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orderObj = OrderDetail.objects.filter(user_id=request.user.id).order_by('-created_at')
        orderData = OrderDetailSerializer(orderObj, many=True).data

        orderList = []

        for i in range(len(orderData)):
            oneOrder = orderData[i]
            orderProductObj = OrderProductDetail.objects.filter(
                order_id=oneOrder["id"])
            orderProductData = OrderProductDetailSerializerD2(
                orderProductObj, many=True).data
            for op in range(len(orderProductData)):
                orderProductData[op]["product"].pop("vendor")
            # orderProductData
            oneOrderFullDetails = {
                "order_details": oneOrder,
                "order_products": orderProductData
            }
            orderList.append(oneOrderFullDetails)

        # try:
        #     orderProductObj = OrderProductDetail.objects.filter(order=orderObj, order__order_status="Order Placed")
        #     orderProductData = OrderProductDetailSerializer(orderProductObj, many=True).data

        #     response = {
        #         "status": "Success",
        #         "orderData": orderData,
        #         "productData": orderProductData
        #     }

        #     return Response(response, status=200)
        # except OrderProductDetail.DoesNotExist:
        #     return Response({"status":"warning", "message":"order not found"}, status=204)
        if len(orderList) > 0:
            return Response({"status": "success", "message": "Order list fetched successfully", "data": orderList},
                            status=200)
        else:
            return Response({"status": "warning", "message": "Opps! You don't have any order", "data": orderList},
                            status=200)


# Customer Address API(get, post)
class CustomerAddressAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        user_address = ContactAddress.objects.filter(user=user)
        user_address_serializer_data = ContactAddressSerializer(
            user_address, many=True).data

        if len(user_address_serializer_data) > 0:
            responseData = {
                "status": "success",
                "message": "Address list found",
                "data": user_address_serializer_data
            }
            return Response(responseData, status=status.HTTP_200_OK)
        else:
            responseData = {
                "status": "warning",
                "message": "You don't have any saved addresses!",
                "data": []
            }
            return Response(responseData, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):

        user = request.user
        customer_name = request.data.get('name', False)
        contactNumber = request.data.get('contact_number', False)
        post_code = request.data.get('postcode', False)
        addressLine = request.data.get('address_line', False)
        locality = request.data.get('locality', False)
        city = request.data.get('city', False)
        state = request.data.get('state', False)
        lat = request.data.get('map_lat', False)
        lng = request.data.get('map_lng', False)
        is_default = request.data.get('is_default', True)
        # save_address_as = request.data.get('save_address_as', False)

        ContactAddress.objects.filter(user=user).update(is_default=False)

        user_contactAddress = ContactAddress.objects.create(user=user,
                                                            name=customer_name,
                                                            contact_number=contactNumber,
                                                            postcode=post_code,
                                                            address_line=addressLine,
                                                            locality=locality,
                                                            city=city,
                                                            state=state,
                                                            map_lat=lat,
                                                            map_lng=lng,
                                                            is_default=is_default,
                                                            )
        user_contactAddress.save()
        responseData = {
            "status": "success",
            "message": "Your Address is Successfully Saved!!",
            "data": {
                "name": customer_name,
                "contact_number": contactNumber,
                "postcode": post_code,
                "address_line": addressLine,
                "locality": locality,
                "city": city,
                "state": state
            }
        }
        return Response(responseData, status=status.HTTP_200_OK)


# User Update Contact Address Api View
class UpdateContactAddressApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def put(self, request, pk):
        user = self.request.user
        user_address = get_object_or_404(ContactAddress, pk=pk)
        if user_address.user != user:
            raise PermissionDenied("This Action You can't Perform!!")

        serializer = ContactAddressSerializer(
            user_address, data=self.request.data, partial=True)

        is_default = self.request.data.get('is_default', False)

        if is_default == True:
            ContactAddress.objects.filter(user=user).update(is_default=False)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        responseData = {
            "status": "success",
            "message": "Your Address is Successfully Updated!!",
            "data": serializer.data
        }
        return Response(responseData, status=status.HTTP_201_CREATED)


# Contact Address Delete API View
class ContactAddressDeleteApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def delete(self, request, pk, format=None):
        address = ContactAddress.objects.get(pk=pk)
        address.delete()
        responseData = {
            "status": "success",
            "message": "Your Address is Successfully deleted!!"
        }
        return Response({"data": responseData}, status=status.HTTP_200_OK)


# Contact Address Delete API View
class DestroyContactAddressAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = ContactAddressSerializer
    queryset = ContactAddress.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        responseData = {
            "status": "success",
            "message": "Your Address is Successfully deleted!!"
        }
        return Response({"detail": responseData}, status=status.HTTP_200_OK)


# This Api is Used for GET, Add
class UserAddressAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userObj = request.user
        try:
            userAddObj = ContactAddress.objects.get(user=userObj)
            jsonData = ContactAddressSerializer(userAddObj, many=False)
            userAddressDetails = jsonData.data
            return Response(
                {"status": "success", "message": "Address fetched successfully",
                 "data": userAddressDetails},
                status=200)
        except ContactAddress.DoesNotExist:
            return Response({"status": "warning", "message": "You don't have an address", "data": []}, status=404)

    def post(self, request):
        userObj = request.user
        regData = request.data
        # regData["user"] = userObj.id

        try:
            userAddObj = ContactAddress.objects.get(user=userObj.id)
            # jsonData = VendorProfileAddressSerializer(vendorAddObj,many=False)
            userAddressSerializer = ContactAddressSerializer(
                userAddObj, data=regData, partial=True)
            if userAddressSerializer.is_valid():
                userAddressSerializer.save()
                return Response({"status": "success", "message": "Address updated successfully"}, status=200)
            else:
                return Response(
                    {"status": "warning", "message": "Invalid inputes",
                     "errors": userAddressSerializer.errors},
                    status=400)
        except ContactAddress.DoesNotExist:
            # userAddressSerializer = ContactAddressSerializer(data=regData)
            # if userAddressSerializer.is_valid():
            #     userAddressSerializer.save()
            #     return Response({"status": "success", "message": "Address added successfully"}, status=201)
            # else:
            #     return Response(
            #         {"status": "warning", "message": "Invalid inputes", "errors": userAddressSerializer.errors},
            #         status=400)
            return Response(
                {"status": "warning", "message": "Invalid inputes",
                 "errors": userAddressSerializer.errors},
                status=400)


# ReturnProductApi
class ReturnProductAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        userObj = self.request.user

        order_Number = request.data.get("order_number", False)
        # userRemark = request.data.get("userRemark", False)
        userRemarkStatus = request.data.get("userRemarkStatus", False)
        returnQty = request.data.get("returnQty", False)
        # productID = request.data.get("id", False)
        orderProductID = request.data.get("id", False)

        # productObj  = Product.objects.get(id=productID)

        orderObj = OrderDetail.objects.get(order_number=order_Number, user=userObj)
        # orderProductObj = OrderProductDetail.objects.get(order=orderObj.id, product=productID)
        orderProductObj = OrderProductDetail.objects.get(id=orderProductID, order=orderObj.id)

        try:
            orderDetailSerializer = OrderDetailSerializers2(orderObj, data=request.data, partial=True)
            if orderDetailSerializer.is_valid():
                orderDetailSerializer.save()

            # orderObj.userRemark = userRemark
            # orderObj.save
            # print(orderObj.userRemark)

            # print(orderProductObj.order)
            # print(orderProductObj.product)
            # orderProductObj.userRemarkStatus = userRemark
            # orderProductObj.save
            # print(orderProductObj.userRemarkStatus)

            if int(returnQty) <= int(orderProductObj.quantity):
                createReturnProduct = ReturnProduct(orderNumber=order_Number,
                                                    orderedProduct=orderProductObj,
                                                    returnQty=returnQty,
                                                    userRemarkStatus=userRemarkStatus,
                                                    )
                createReturnProduct.save()
            else:
                return Response({
                    "status": "warning",
                    "message": "Please enter the Right quantity!!",
                }, status=status.HTTP_200_OK)

        except OrderDetail.DoesNotExist:
            return Response({
                "status": "warning",
                "message": "Order id not valid"
            }, status=status.HTTP_400_BAD_REQUEST)

        responseData = {
            "status": "success",
            "Return Product Id": createReturnProduct.return_id,
            "message": "User Order Remark Updated Successfuly",

        }
        return Response(responseData, status=status.HTTP_200_OK)


# Return Product History
class OrderReturnProductHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReturnProductSerializer
    queryset = ReturnProduct.objects.all().order_by('-id')
