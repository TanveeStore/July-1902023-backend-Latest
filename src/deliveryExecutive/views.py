from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from common.models import User
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import hashlib
import time
from django.core.exceptions import ObjectDoesNotExist
from phonenumber_field.modelfields import PhoneNumberField
from django.core.mail import send_mail
from Notifications.models import Notifications
from common.utils import CommonUtils

from .models import DeliveryExecutive
from .serializers import (DeliveryExeLoginSerializer, DeliveryExeChangePasswordSerializer,
                          DeliveryExeProfileBasicSerializer, DeliveryExeProfileBusinessSerializer,
                          DeliveryExeProfileStatusSerializer, DeliveryExeLiveDataSerializer,
                          DeliveryExeOrderDetailsSerializer)

from orders.models import OrderDetail, OrderProductDetail, DeliveryExeLiveData, VendorOrderDetails
from orders.serializers import (VendorOrderDetailsSerializer, OrderProductDetailSerializer,
                                OrderDetailSerializer, VendorOrderDetailsSerializerD0,
                                VendorOrderDetailsSerializerD1, VendorOrderDetailsSerializerD2)
from vendor.serializers import VendorOrderProductDetailSerializer, VendorProfileAddressSerializer

from vendor.models import VendorAddress


class deliveryExecutiveHelper():
    def getDeliveryExecutiveLiveData(self, deliveryExecutiveId):
        pass


# Create your views here.
# [POST] http://127.0.0.1:8000/api/delivery-executive/login/  DONE
# [REQUEST]:
# {
#     "email":"delivery@gmail.com",
#     "password":"Test@786"
# }
# [RESPONSE]:
# {
#     "status": "success",
#     "message": "login successful",
#     "data": {
#         "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjUwNDM2MDU4LCJpYXQiOjE2NTAxNzY4NTgsImp0aSI6ImQ5YTNlM2U2MmM0MjQ4NGViN2VhMmYzYjJjNTRkYjViIiwidXNlcl9pZCI6MTB9.-PiYauf-vBxXf_6LEEfkQ4lF55XJ8QfjgDpuyu43M90",
#         "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY1MDQzNjA1OCwiaWF0IjoxNjUwMTc2ODU4LCJqdGkiOiIzM2FkYzBiNGYxODY0ZWRkYTBjMDJmYzk4NGIyN2E2ZSIsInVzZXJfaWQiOjEwfQ._UZkGUDYxJJ0DT9Jg2WUl-kpnFYs7xuCEbQ2Jxb_k44"
#     }
# }
class DeliveryExeLoginAPIview(APIView):
    def get(self, request):
        return Response({"status": "success"}, status=200)

    def post(self, request, *args, **kwargs):
        deliveryExeLoginSerializer = DeliveryExeLoginSerializer(
            data=request.data)
        if deliveryExeLoginSerializer.is_valid():
            email = request.data.get('email', False)
            password = request.data.get('password', False)
            check_email = User.objects.filter(
                email=email, role="executive_user").first()
            if check_email:
                user = authenticate(email=email, password=password)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "status": "success",
                        "message": "login successful",
                        "data": {"access": str(refresh.access_token), "refresh": str(refresh)}
                    }, status=200)
                else:
                    return Response({"status": "warning", "message": "Invalid credentials"}, status=401)
            else:
                return Response({"status": "warning", "message": "Email does not exist!"}, status=401)

        return Response({"status": "warning", "message": "Invalid inputes!", "errors": deliveryExeLoginSerializer.errors}, status=400)


# [POST] http://127.0.0.1:8000/api/delivery-executive/change-password/ OK
# [REQUEST]
# {
#     "old_password":"Test@7866",
#     "new_password":"Test@786"
# }
# [RESPONSE]:
# {
#     "status": "warning",
#     "message": "Old password is incorrect!!"
# }
class DeliveryExeChangePasswordAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        changePasswordSerializer = DeliveryExeChangePasswordSerializer(
            data=request.data)
        if changePasswordSerializer.is_valid():
            if self.request.user.check_password(request.data["old_password"]):
                self.request.user.set_password(
                    changePasswordSerializer.data.get("new_password"))
                self.request.user.save()
                return Response({"status": "success", "message": "Password changed success"}, status=200)
            return Response({"status": "warning", "message": "Old password is incorrect!!"}, status=401)
        return Response({"status": "warning", "message": "Invalid inputes", "errors": changePasswordSerializer.errors}, status=400)


# [GET] http://127.0.0.1:8000/api/delivery-executive/profile/status/    OK

class DeliveryExeProfileStatusAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            deliveryExeObj = DeliveryExecutive.objects.get(
                user=self.request.user)
            jsonData = DeliveryExeProfileStatusSerializer(
                deliveryExeObj, many=False)
            deliveryExeStatusDetails = jsonData.data

            return Response({"status": "success", "message": "Delivery Exe. Profile Status fetched successfully", "data": deliveryExeStatusDetails}, status=200)

        except DeliveryExecutive.DoesNotExist:
            return Response({
                "status": "warning",
                "message": "Business profile not found",
                "data": {
                            "status": "incomplete"
                            }
            }, status=404)


class DeliveryExeProfileBasicAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        jsonData = DeliveryExeProfileBasicSerializer(userObj)
        deliveryProfile = jsonData.data
        return Response({"status": "success", "message": "Basic Profile fetched successfully", "data": deliveryProfile}, status=200)

    def post(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        basicProfileSerializer = DeliveryExeProfileBasicSerializer(
            userObj, data=request.data, partial=True)
        if basicProfileSerializer.is_valid():
            basicProfileSerializer.save()
            return Response({"status": "success", "message": "Basic Profile updated successfully"}, status=200)
        else:
            return Response({"status": "warning", "message": "Invalid inputes", "errors": basicProfileSerializer.errors}, status=400)


class DeliveryExeProfileBusinessAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        deliveryExeObj = DeliveryExecutive.objects.get(
            user_id=self.request.user.id)
        jsonData = DeliveryExeProfileBusinessSerializer(
            deliveryExeObj, many=False)
        deliveryExeBusinessDetails = jsonData.data
        return Response({"status": "success", "message": "Bunisess Profile fetched successfully", "data": deliveryExeBusinessDetails}, status=200)

    def post(self, request):
        deliveryExeObj = DeliveryExecutive.objects.get(
            user_id=self.request.user.id)
        deliveryExeBusinessSerializer = DeliveryExeProfileBusinessSerializer(
            deliveryExeObj, data=request.data, partial=True)
        if deliveryExeBusinessSerializer.is_valid():
            deliveryExeBusinessSerializer.save()
            return Response({"status": "success", "message": "Business Profile updated successfully"}, status=200)
        else:
            return Response({"status": "warning", "message": "Invalid inputes", "errors": deliveryExeBusinessSerializer.errors}, status=400)


class DeliveryExeOrderList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, filterName):
        deliveryExeObj = DeliveryExecutive.objects.get(user_id=request.user.id)

        try:
            filterType = "All"

            if filterName == "cancelled":
                filterType = "Cancelled"
                userOrderObj = OrderDetail.objects.filter(
                    delivery_exe=deliveryExeObj, order_status="Cancelled").order_by("-id")
            elif filterName == "present-orders":
                filterType = "Order placed and On The Way"
                userOrderObj = OrderDetail.objects.filter(delivery_exe=deliveryExeObj, order_status__in=['On The Way', 'Order Placed']).order_by("-id") 
            elif filterName == "delivered":
                filterType = "Delivered"
                userOrderObj = OrderDetail.objects.filter(
                    delivery_exe=deliveryExeObj, order_status="Delivered").order_by("-id")
            else:
                userOrderObj = OrderDetail.objects.filter(
                    delivery_exe=deliveryExeObj).order_by("-id")

            userOrderDetailsData = OrderDetailSerializer(
                userOrderObj, many=True).data
            if(len(userOrderDetailsData) > 0):
                return Response({"status": "success", "message": filterType+" order list fetched success", "data": userOrderDetailsData}, status=200)
            else:
                return Response({"status": "warning", "message": "You don't have any '" + filterType + "' orders"}, status=204)

        except OrderDetail.DoesNotExist:
            return Response({"status": "warning", "message": "You don't have any order!", "data": []}, status=204)


class DeliveryExeOrderDetails(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        orderId = pk
        deliveryExeObj = DeliveryExecutive.objects.get(user_id=request.user.id)

        try:
            userOrderObj = OrderDetail.objects.get(
                delivery_exe=deliveryExeObj, id=orderId)  # nothing but a cross check
            orderDetailsData = OrderDetailSerializer(
                userOrderObj, many=False).data

            vendorOrderObj = VendorOrderDetails.objects.filter(
                order=userOrderObj)
            vendorOrdersList = VendorOrderDetailsSerializerD0(
                vendorOrderObj, many=True).data

            for i in range(len(vendorOrdersList)):
                oneVendorOrder = vendorOrdersList[i]

                vendorAddressObj = VendorAddress.objects.get(
                    vendor_id=oneVendorOrder["vendor"])
                vendorAddressData = VendorProfileAddressSerializer(
                    vendorAddressObj, many=False).data

                vendorOrdersList[i]["vendor_address"] = vendorAddressData

                # Vendor Order Product list
                vendorOrderProductObj = OrderProductDetail.objects.filter(
                    order_id=oneVendorOrder["order"], product__vendor_id=oneVendorOrder["vendor"])
                vendorOrderProductData = VendorOrderProductDetailSerializer(
                    vendorOrderProductObj, many=True).data
                for vp in range(len(vendorOrderProductData)):
                    vendorOrderProductData[vp].pop("order")
                    vendorOrderProductData[vp]["product"].pop("vendor")

                vendorOrdersList[i]["vendor_products"] = vendorOrderProductData

            #oneVendorOrderData = vendorOrderObjData

            responseData = {
                "orderDetails": orderDetailsData,
                "vendorList": vendorOrdersList
            }

            return Response({"status": "success", "message": "Order full details fetched success", "data": responseData}, status=200)

        except OrderDetail.DoesNotExist:
            return Response({"status": "warning", "message": "You don't have any order!", "data": []}, status=204)


class DeliveryExeLiveLocationData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        deliveryExeObj = DeliveryExecutive.objects.get(user_id=request.user.id)
        try:
            deliveryExeLiveDataObj = DeliveryExeLiveData.objects.get(
                delivery_exe=deliveryExeObj)
            deliveryExeLiveJsonData = DeliveryExeLiveDataSerializer(
                deliveryExeLiveDataObj, many=False).data
            deliveryExeLiveJsonData.pop("delivery_exe")
            return Response({"status": "success", "message": "Live data fetched success", "data": deliveryExeLiveJsonData}, status=200)
        except DeliveryExeLiveData.DoesNotExist:
            return Response({"status": "warning", "message": "You don't have any live data", "data": []}, status=204)

    def post(self, request):
        deliveryExeObj = DeliveryExecutive.objects.get(user_id=request.user.id)
        print(deliveryExeObj)
        deliveryExeLiveDataSerializerObj = DeliveryExeLiveDataSerializer(
            data=request.data, partial=True)
        if deliveryExeLiveDataSerializerObj.is_valid():
            try:
                deliveryExeLiveDataObj = DeliveryExeLiveData.objects.get(
                    delivery_exe=deliveryExeObj)
                deliveryExeLiveDataUpdate = DeliveryExeLiveDataSerializer(
                    deliveryExeLiveDataObj, data=request.data, partial=True)
                if deliveryExeLiveDataUpdate.is_valid():
                    deliveryExeLiveDataUpdate.save()
                    return Response({"status": "success", "message": "Live data update success"}, status=201)

            except DeliveryExeLiveData.DoesNotExist:
                reqData = request.data
                reqData["delivery_exe"] = deliveryExeObj.id

                deliveryExeLiveDataSerializerObj = DeliveryExeLiveDataSerializer(
                    data=reqData)
                if deliveryExeLiveDataSerializerObj.is_valid():
                    deliveryExeLiveDataSerializerObj.save()

                    return Response({"status": "success", "message": "Live data added success"}, status=201)
                else:
                    return Response({"status": "warning", "message": "errors", "errors": deliveryExeLiveDataSerializerObj.errors}, status=400)
        else:
            return Response({"status": "warning", "message": "Invalid inputs", "errors": deliveryExeLiveDataSerializerObj.errors}, status=400)


class DeliveryExeOrdersStatusChangeForCustomer(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        userObj = User.objects.get(id=request.user.id)
        
        deliveryExeObj = DeliveryExecutive.objects.get(user_id=request.user.id)

        order_id = request.data.get("order_id", None)
        order_status = request.data.get("order_status", None)
        orderDetailsObj = OrderDetail.objects.get(id=order_id)
        customerObj = User.objects.get(id=orderDetailsObj.user.id)
        # order_status = Pending, Order Placed, On The Way, Delivered, Cancelled

        if order_id != None and order_status != None:
            try:
                orderDetailObj = OrderDetail.objects.get(
                    id=order_id, delivery_exe_id=deliveryExeObj.id)
                orderDetailObj.order_status = order_status
                orderDetailObj.save()

                # Customer OrderStatus Sms
                textMessage = f'Hello {customerObj.first_name}, Thank you for keeping patience with us , Your order {orderDetailsObj.order_number} has been {orderDetailObj.order_status} at your doorstep. see you soon , Team Tanvee Store' 
                orderDeliveryResponse = CommonUtils.SendMobileMessage([customerObj.mobile], "order-delivered", textMessage)
                
                # Customer OrderStatus Notification
                customerNotificationObj = Notifications.objects.create(user=customerObj,
                                                        notificationText=textMessage,
                                                        notificationType ="order",
                                                        seenStatus=False)
                customerNotificationObj.save()

                # CommonUtils.sendPushNotification(userType="customer", fcmTokens=[customerObj.fcm_token], title="Tanvee Notification", msg=textMessage, image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb", dataObject=None)
                
                # DeliveryExecutive OrderStatus Notification
                deliveryExNotificationMessage = f'Hello {userObj.first_name}, Your Delivery Order #{orderDetailsObj.order_number} Status is {orderDetailObj.order_status}'
                deliveryExNotificationObj = Notifications.objects.create(user=userObj,
                                                        notificationText=deliveryExNotificationMessage,
                                                        notificationType ="order",
                                                        seenStatus=False)
                deliveryExNotificationObj.save()

                CommonUtils.sendPushNotification(userType="deliveryExecutive", fcmTokens=[userObj.fcm_token], title="Tanvee Notification", msg=deliveryExNotificationMessage, image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb", dataObject=None)

                return Response({"status": "success", "message": "Customer order status changed success"}, status=200)
            except OrderDetail.DoesNotExist:
                return Response({"status": "warning", "message": "Invalid order id"}, status=200)
        else:
            return Response({"status": "warning", "message": "Invalid inputes"}, status=200)


class DeliveryExeOrdersStatusChangeForVendor(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id", None)
        vendor_id = request.data.get("vendor_id", None)
        order_status = request.data.get("order_status", None)

        # order_status = Pending, Order Placed, On The Way, Delivered, Cancelled

        if order_id != None and vendor_id != None and order_status != None:
            try:
                vendorOrderDetailsObj = VendorOrderDetails.objects.get(
                    order_id=order_id, vendor_id=vendor_id)
                vendorOrderDetailsObj.order_status = order_status
                vendorOrderDetailsObj.save()

                vendorNotificationMessage = f'Hello {vendorOrderDetailsObj.vendor.org_name}, The Product has been ordered by Customer , The order {vendorOrderDetailsObj.order.order_number} has been {vendorOrderDetailsObj.order_status} by Delivery Executive. see you soon , Team Tanvee Store'
                vendorNotificationObj = Notifications.objects.create(user=vendorOrderDetailsObj.vendor.user,
                                                        notificationText=vendorNotificationMessage,
                                                        notificationType ="other",
                                                        seenStatus=False)
                vendorNotificationObj.save()

                CommonUtils.sendPushNotification(userType="vendor", fcmTokens=[vendorOrderDetailsObj.vendor.user.fcm_token], title="Tanvee Notification", msg=vendorNotificationMessage, image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb", dataObject=None)
                return Response({"status": "success", "message": "Status changed success"}, status=200)
            except VendorOrderDetails.DoesNotExist:
                return Response({"status": "warning", "message": "Invalid order details"}, status=200)
        else:
            return Response({"status": "warning", "message": "Invalid inputes"}, status=200)
