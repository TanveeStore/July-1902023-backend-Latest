from itertools import count, product
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Sum
from django.conf import settings
from common.models import Profile, User
from .models import (Vendor, User, VendorAddress, VendorBankAccount)
from .serializers import (VendorRegSerializer,
                          VendorLoginSerializer,
                          VendorChangePasswordSerializer,
                          VendorProfileBasicSerializer,
                          VendorProfileBusinessSerializer,
                          VendorProfileBusinessSerializerUpdate,
                          VendorProfileBasicSerializerUpdate,
                          VendorProfileStatusSerializer,
                          VendorProfileAddressSerializer,
                          VendorProfileBankAccountSerializer,
                          VendorProductPostSerializer,
                          VendorProductGetSerializer,
                          VendorProductImageGetSerializer,
                          VendorOrderProductDetailSerializer,
                          VendorOrderDetailSerializer)

from orders.models import VendorOrderDetails
from  orders.serializers import VendorOrderDetailsSerializer

from products.models import Product, ProductImage
from products.serializers import ProductImageSerializer
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import hashlib, time
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from orders.models import OrderDetail, OrderProductDetail
from orders.serializers import OrderDetailSerializer, OrderProductDetailSerializer

from common.utils import CommonUtils
import random

# Create your views here.

# [POST] http://127.0.0.1:8000/api/vendor/registration/    DONE
# [REQUEST]
# {
#     "first_name":"Rachhel",
#     "last_name":"Sekh",
#     "gender":"Male",
#     "org_name":"Xyz Pvt Ltd",
#     "pancard":"HMMPSOWW02",
#     "mobile":"+919988009990",
#     "email":"dev.rachhel@gmail.com"
# }
# [RESPONSE]:
# {
#     "status": "warning",
#     "message": "Invalid inputes!",
#     "errors": {
#         "email": [
#             "Email already exists!"
#         ]
#     }
# }

class VendorRegistrationAPIview(APIView):
    def get(self, request):
        return Response({"status": "success","message":"success"}, status=200)
    
    def post(self, request, *args, **kwargs):

        email = request.data.get('email', False)
        mobile = request.data.get('mobile', False)
        first_name = request.data.get('first_name', False)
        last_name = request.data.get('last_name', False)

        vendorRegSerializer=VendorRegSerializer(data=request.data)
        if vendorRegSerializer.is_valid():
            # tempPassword="Test@786"
            otp = str(random.randint(1234, 9999))
            tempPassword = first_name+"@"+otp
            user = User(email=email, first_name = first_name, last_name = last_name, mobile = mobile, role="vendor")
            user.set_password(tempPassword)
            user.save()
            vendor = Vendor(user=user, org_name=request.data['org_name'])
            vendor.save()
            
            profile = Profile(user=user, role="vendor")
            print(profile)
            profile.save()

            print("Vendor Temp Password : "+tempPassword)

            # Get the SuperUser Details by is_superuser=True 
            superusers = User.objects.get(is_superuser=True)
            print(superusers.email)

            try:

                # textMessage = f'Welcome to Tanvee Rythu Store Family.Your temporary password is {tempPassword}'
                # otpResponse = CommonUtils.SendMobileMessage(
                #     [mobile], "otp", textMessage)
                # if otpResponse == True:
                #     return Response({"status": "success", "message": "Registration success! Temporary password has been sent to your mobile."}, status=200)
                # else:
                #     return Response({"status": "warning", "message": "Opps! Temporary password send fail, Try again!!"}, status=200)

                # Send Email to Vendor
                mailSubject="Welcome to Tanvee!!!"
                mailMessage = "Hello "+first_name+"! Thanks for joining with us. Your username: "+email+" and your temporary password: "+tempPassword+" . Please Change your password and login to your account to complete Your Business Profile. Thanks Again! Happy Business! Tanvee Admin will get back to you soon. | Team Tanvee Store"
                # mailFrom="dev.rachhel@gmail.com"
                mailFrom=settings.EMAIL_HOST_USER
                mailTo=[email]
                send_mail(mailSubject,mailMessage,mailFrom,mailTo,fail_silently=False)

                # send Email to SuperUser 
                superuser_mailMessage = "Hello " + superusers.first_name + " " + superusers.last_name + " new vendor " +first_name+ " "+last_name+ " | " +mobile+ " Sending this request for approval to do Business. please check all the details of Vendor on Admin Portal and approve it."
                mailtoSuperUser = [superusers.email]
                send_mail(mailSubject,superuser_mailMessage,mailFrom,mailtoSuperUser, fail_silently=False)

                return Response({"status":"success","message":"Register success! Thanks for joining with us Please complete Your Business Profile. Tanvee Admin will get back to you soon. Please Check your email for Username and Password. | Team Tanvee Store"},status=200)
            except:
                return Response({"status":"success","message":"Register success!", "error":"Email send fail, Email temporary password: "+tempPassword},status=200)
                #return Response({"status":"success","message":"Registration success! Temporary password sent fail!!!"},status=200)
            

        else:
            return Response({"status":"warning","message":"Invalid inputes!","errors":vendorRegSerializer.errors},status=400)




# [POST] http://127.0.0.1:8000/api/vendor/login/  DONE
# [REQUEST]:
# {
#     "email":"rachhel.sekh@achievexsolutions.com",
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
class VendorLoginAPIview(APIView):
    def get(self, request):
        return Response({"status": "success","message":"login api"},status=200)
    
    def post(self, request, *args, **kwargs):
        vendorLoginSerializer = VendorLoginSerializer(data=request.data)
        if vendorLoginSerializer.is_valid():
            email = request.data.get('email', False)
            password = request.data.get('password', False)
            check_email = User.objects.filter(email=email).first()
            if check_email:
                user = authenticate(email=email, password=password)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "status": "success",
                        "message":"login successful",
                        "data": {"access": str(refresh.access_token),"refresh": str(refresh)}
                        },status=200)
                else:
                   return Response({"status": "warning","message":"Invalid credentials"},status=401)
            else:
                return Response({"status": "warning","message":"Email does not exist!"},status=401)
            
        return Response({"status": "warning","message":"Invalid inputes!","errors":vendorLoginSerializer.errors},status=400)



# [POST] http://127.0.0.1:8000/api/vendor/change-password/    DONE
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

class VendorChangePasswordAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        changePasswordSerializer = VendorChangePasswordSerializer(data=request.data)
        if changePasswordSerializer.is_valid():
            if self.request.user.check_password(request.data["old_password"]):
                self.request.user.set_password(changePasswordSerializer.data.get("new_password"))
                self.request.user.save()
                return Response({"status": "success","message":"Password changed success"},status=200)
            return Response({"status": "warning","message":"Old password is incorrect!!"},status=401)
        return Response({"status": "warning","message":"Invalid inputes","errors":changePasswordSerializer.errors},status=400)


#Profile
#[GET] http://127.0.0.1:8000/api/vendor/profile/basic/    DONE [IN POST REQUEST YOU HAVE TO PUT THE ALL VALUES IN FORM/DATA ENCRYPTION]
#[RESPONSE]:
# {
#     "status": "success",
#     "message": "Basic Profile fetched successfully",
#     "data": {
#         "id": 12,
#         "first_name": "Rachhel",
#         "last_name": "Sekh",
#         "gender": "male",
#         "email": "rachhel.sekh@achievexsolutions.com",
#         "alternate_email": null,
#         "mobile": "+919988009990",
#         "is_active": true,
#         "date_joined": "2022-04-18T05:48:56.479678Z",
#         "profile_pic": "/static/profile_pic/Screenshot_3_6YDGmVd.png"
#     }
# }

class VendorProfileBasicAPIview(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        userObj=User.objects.get(id=self.request.user.id)
        jsonData = VendorProfileBasicSerializer(userObj)
        vendorProfile = jsonData.data
        return Response({"status": "success","message":"Basic Profile fetched successfully","data":vendorProfile},status=200)
    
    def post(self, request):
        userObj=User.objects.get(id=self.request.user.id)
        basicProfileSerializer = VendorProfileBasicSerializerUpdate(userObj,data=request.data, partial=True)
        if basicProfileSerializer.is_valid():
            basicProfileSerializer.save()
            return Response({"status": "success","message":"Basic Profile updated successfully"},status=200)
        else:
            return Response({"status": "warning","message":"Invalid inputes","errors":basicProfileSerializer.errors},status=400)
    


#[POST] http://127.0.0.1:8000/api/vendor/profile/business/    DONE
#[REQUEST]: [form/data]
# {
#     "org_name": "Xyz Pvt Ltd 2",
#     "telephone_1": "+919876543456",
#     "telephone_2": "+918765678987",
#     "company_pancard": "HHGVY77309",
#     "company_pancard_doc": <File>,
#     "adhar_udyam_udoyog": "AD83CNUEN C32",
#     "adhar_udyam_udoyog_doc": <File>,
#     "gst_number": "GSHS007678987"
# }
#[RESPONSE]:
# {
#     "status": "success",
#     "message": "Business Profile updated successfully"
# }
#
# [GET] http://127.0.0.1:8000/api/vendor/profile/business/    DONE 
# [RESPONSE]:
# {
#     "status": "success",
#     "message": "Bunisess Profile fetched successfully",
#     "data": {
#         "org_name": "Xyz Pvt Ltd 2",
#         "telephone_1": "+919876543456",
#         "telephone_2": "+918765678987",
#         "company_pancard": "HHGVY77309",
#         "company_pancard_doc": "/static/documents/vendor/pancard/Screenshot_5.png",
#         "adhar_udyam_udoyog": "AD83CNUEN C32",
#         "adhar_udyam_udoyog_doc": "/static/documents/vendor/aadhaar/Screenshot_7.png",
#         "gst_number": "GSHS007678987"
#     }
# }
class VendorProfileBusinessAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        vendorObj=Vendor.objects.get(user_id=self.request.user.id)
        jsonData = VendorProfileBusinessSerializer(vendorObj,many=False)
        vendorBusinessDetails = jsonData.data
        return Response({"status": "success","message":"Bunisess Profile fetched successfully","data":vendorBusinessDetails},status=200)
    
    def post(self, request):
        vendorObj=Vendor.objects.get(user_id=self.request.user.id)
        vendorBusinessSerializer = VendorProfileBusinessSerializerUpdate(vendorObj,data=request.data, partial=True)
        if vendorBusinessSerializer.is_valid():
            vendorBusinessSerializer.save()
            return Response({"status": "success","message":"Business Profile updated successfully"},status=200)
        else:
            return Response({"status": "warning","message":"Invalid inputes","errors":vendorBusinessSerializer.errors},status=400)


#[GET] http://127.0.0.1:8000/api/vendor/profile/business/    DONE
#[RESPONSE]:
# {
#     "status": "success",
#     "message": "Vendor Profile Status fetched successfully",
#     "data": {
#         "status": "incomplete"
#     }
# }

class VendorProfileStatusAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        vendorObj=Vendor.objects.get(user=self.request.user)
        jsonData = VendorProfileStatusSerializer(vendorObj,many=False)
        vendorStatusDetails = jsonData.data
        
        return Response({"status": "success","message":"Vendor Profile Status fetched successfully","data":vendorStatusDetails},status=200)


# [GET] http://127.0.0.1:8000/api/vendor/profile/bank-details/ OK
# [POST] http://127.0.0.1:8000/api/vendor/profile/bank-details/ OK
# [REQUEST]:
# {
#     "acc_bank_name": "HDFC2",
#     "acc_branch_name": "Kolkata",
#     "acc_ifsc": "HDFC008952",
#     "acc_no": 7878848484
# }
# [RESPONSE]:
# {
#     "status": "success",
#     "message": "Bank added successfully"
# }

class VendorProfileBankDetailsAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        vendorObj=Vendor.objects.get(user_id=self.request.user.id)
        try:
            vendorBankObj=VendorBankAccount.objects.get(vendor=vendorObj.id)
            jsonData = VendorProfileBankAccountSerializer(vendorBankObj,many=False)
            vendorBankDetails = jsonData.data
            return Response({"status": "success","message":"Bank details fetched successfully","data":vendorBankDetails},status=200)
        except VendorBankAccount.DoesNotExist:
            return Response({"status": "warning","message":"You don't have any Bank details", "data":[]},status=200)

    def post(self, request):
        vendorObj=Vendor.objects.get(user_id=self.request.user.id)
        regData=request.data
        regData["vendor"]=vendorObj.id
        regData["is_default"]=True
        try:
            vendorBankObj=VendorBankAccount.objects.get(vendor=vendorObj.id)
            vendorBankSerializer = VendorProfileBankAccountSerializer(vendorBankObj,data=regData,partial=True)
            if vendorBankSerializer.is_valid():
                vendorBankSerializer.save()
                return Response({"status": "success","message":"Bank details updated successfully"},status=200)
            else:
                return Response({"status": "warning","message":"Invalid inputes","errors":vendorBankSerializer.errors},status=400)
        except VendorBankAccount.DoesNotExist:
            vendorBankSerializer = VendorProfileBankAccountSerializer(data=regData)
            if vendorBankSerializer.is_valid():
                vendorBankSerializer.save()
                return Response({"status": "success","message":"Bank added successfully"},status=201)
            else:
                return Response({"status": "warning","message":"Invalid inputes","errors":vendorBankSerializer.errors},status=400)
            
 


#[GET] http://127.0.0.1:8000/api/vendor/profile/address/    DONE
#[POST] http://127.0.0.1:8000/api/vendor/profile/address/    DONE
# [REQUEST]:
# {
#     "name":"Rachhel",
#     "address":"Barasat",
#     "locality":"Barasat",
#     "city":"Barasat",
#     "state":"West Bengal",
#     "postcode":"kjbhbh",
#     "map_lat":"45.484444",
#      "map_lng":"78.51544"
# }
# [RESPONSE]
# {
#     "status": "success",
#     "message": "Address updated successfully"
# }

class VendorProfileAddressAPIview(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        vendorObj=Vendor.objects.get(user_id=self.request.user.id)
        try:
            vendorAddObj=VendorAddress.objects.get(vendor=vendorObj.id)
            jsonData = VendorProfileAddressSerializer(vendorAddObj,many=False)
            vendorAddressDetails = jsonData.data
            return Response({"status": "success","message":"Address fetched successfully","data":vendorAddressDetails},status=200)
        except VendorAddress.DoesNotExist:
            return Response({"status": "warning","message":"You don't have an address", "data":[]},status=200)

    def post(self, request):
        vendorObj=Vendor.objects.get(user_id=self.request.user.id)
        regData=request.data
        regData["vendor"]=vendorObj.id

        try:
            vendorAddObj=VendorAddress.objects.get(vendor=vendorObj.id)
            #jsonData = VendorProfileAddressSerializer(vendorAddObj,many=False)
            vendorAddressSerializer = VendorProfileAddressSerializer(vendorAddObj,data=regData,partial=True)
            if vendorAddressSerializer.is_valid():
                vendorAddressSerializer.save()
                return Response({"status": "success","message":"Address updated successfully"},status=200)
            else:
                return Response({"status": "warning","message":"Invalid inputes","errors":vendorAddressSerializer.errors},status=400)
        except VendorAddress.DoesNotExist:
            vendorAddressSerializer = VendorProfileAddressSerializer(data=regData)
            if vendorAddressSerializer.is_valid():
                vendorAddressSerializer.save()
                return Response({"status": "success","message":"Address added successfully"},status=201)
            else:
                return Response({"status": "warning","message":"Invalid inputes","errors":vendorAddressSerializer.errors},status=400)
            

# Product Created, Updated , Deleted, Retrive By Vendor
class VendorProductDetailsAPIview(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        vendorProductObj = Product.objects.filter(vendor=vendorObj.id)
        vendorProductSerializer = VendorProductGetSerializer(vendorProductObj, many=True)

        return Response({"status": "success", "data": vendorProductSerializer.data})
    
    def post(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        reqData = request.data.copy()
        reqData["vendor"] = vendorObj.id
        serializerData = VendorProductPostSerializer(data=reqData, partial=False)
        if serializerData.is_valid():
            serializerData.save()
            return Response({"status": "success", "message": "Product added successfully!!!"},status=200)
        else:
            return Response({"status": "warning", "message": "Invalid inputes", "errors": serializerData.errors},status=400)

    def patch(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        reqData = request.data.copy()
        reqData["vendor"] = vendorObj.id
        productId = reqData["id"]

        try:
            productObj = Product.objects.get(id=productId, vendor=vendorObj)
            serializerData = VendorProductPostSerializer(productObj, data=reqData, partial=True)
            if serializerData.is_valid():
                serializerData.save()
                return Response({"status": "success", "message": "Product update successfully!!!"}, status=200)
            else:
                return Response({"status": "warning", "message": "Product update fail!!!","errors":serializerData.errors}, status=200)
        except Product.DoesNotExist:
            return Response({"status": "warning", "message": "Product not found!!!"}, status=200)

    def delete(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        reqData = request.data.copy()
        reqData["vendor"] = vendorObj.id
        productId = reqData["id"]

        try:
            productObj = Product.objects.get(id=productId, vendor=vendorObj).delete()
            return Response({"status": "success", "responseData": "product deleted Successfully!!!"})

        except Product.DoesNotExist:
            return Response({"status": "warning", "message": "Product not found!!!"}, status=200)


# Multiple Images of Product ApiView
class VendorProductImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        vendorProductImageObj = ProductImage.objects.filter()
        vendorProductImageSerializer = ProductImageSerializer(vendorProductImageObj, many=True)

        return Response({"status": "success", "data": vendorProductImageSerializer.data})

    def post(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        reqData = request.data.copy()
        reqData["vendor"] = vendorObj.id
        serializerData = ProductImageSerializer(data=reqData, partial=False)
        if serializerData.is_valid():
            serializerData.save()
            return Response({"status": "success", "message": "Product Image added successfully!!!"},status=200)
        else:
            return Response({"status": "warning", "message": "Invalid inputes", "errors": serializerData.errors},status=200)


    def patch(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        reqData = request.data.copy()
        reqData["vendor"] = vendorObj.id
        productId = reqData["id"]

        try:
            productObj = ProductImage.objects.get(id=productId)
            serializerData = ProductImageSerializer(productObj, data=reqData, partial=True)
            if serializerData.is_valid():
                serializerData.save()
                return Response({"status": "success", "message": "Product Image update successfully!!!"},status=200)
            else:
                return Response({"status": "warning", "message": "Product Image update fail!!!"},status=200)
        except ProductImage.DoesNotExist:
            return Response({"status": "warning", "message": "Product Image not found!!!"}, status=200)


    def delete(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        reqData = request.data.copy()
        reqData["vendor"] = vendorObj.id
        productImageId = reqData["id"]

        try:
            productObj = ProductImage.objects.get(id=productImageId).delete()
            return Response({"status": "success", "responseData": "product deleted Successfully!!!"}, status=200)

        except ProductImage.DoesNotExist:
            return Response({"status": "warning", "message": "Product Image not found!!!"}, status=200)

class VendorOrderRecentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        try:
            vendorOrderObj = VendorOrderDetails.objects.filter(vendor=vendorObj, order__order_status="Order Placed").order_by("-id")[:1]
            #orderProductObj = OrderProductDetail.objects.filter(product__vendor=vendorObj, order__order_status="Order Placed")
            vendorOrderDetailsData = VendorOrderDetailsSerializer(vendorOrderObj, many=True).data
            return Response({"status": "success", "message": "Recent order fetched success!", "data": vendorOrderDetailsData}, status=200)
        except VendorOrderDetails.DoesNotExist:
            return Response({"status": "warning", "message": "You don't have any order!", "data":[]}, status=200)
        # orderDetailsList = []
        # orderNoList = []
        # for oneProduct in orderProductDetails:
        #     orderNo = oneProduct["order"]["order_number"]
        #     if orderNo not in orderNoList:
        #         orderNoList.append(orderNo)
        #         orderObj = OrderDetail.objects.get(order_number = orderNo)
        #         orderDetailsData = VendorOrderDetailSerializer(orderObj, many=False).data
        #         orderDetailsList.append(orderDetailsData)
        #

        print(vendorOrderDetailsData)
        # allRecentOrderList = []
        # for oneOrderNo in orderNoList:
        #     print(oneOrderNo)
        #     orderObj = OrderDetail.objects.filter(order_number = "ORD36443290167")
        #     orderDetailsData = VendorOrderDetailSerializer(orderObj, many=False).data
        #     print(orderDetailsData)
        #     allRecentOrderList.append(orderDetailsData)



class VendorOrderHistoryAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        try:
            vendorOrderObj = VendorOrderDetails.objects.filter(vendor=vendorObj, order__order_status="Order Placed").order_by("-id")
            # orderProductObj = OrderProductDetail.objects.filter(product__vendor=vendorObj, order__order_status="Order Placed")
            vendorOrderDetailsData = VendorOrderDetailsSerializer(vendorOrderObj, many=True).data
            print(len(vendorOrderDetailsData))

            responseData = []
            # for i in range(len(vendorOrderDetailsData)):
            #     vendorDetails = vendorOrderDetailsData[i]["vendor"]["user"]
            #     userAddressDetails = vendorOrderDetailsData[i]["order"]["address"]
            #     deliveryExeDetails = vendorOrderDetailsData[i]["order"]["delivery_exe"]

            #     vendorDetails.pop("password")
            #     userAddressDetails.pop("user")
            #     #deliveryExeDetails["user"].pop("password")

            #     tempData = {
            #         "vendor_details" : vendorDetails,
            #         "customer_address" : userAddressDetails,
            #         "delivery_executive" : deliveryExeDetails
            #     }
            #     responseData.append(tempData)

            return Response({"status": "success", "message": "Order details fetched success","data": vendorOrderDetailsData}, status=200)

        except VendorOrderDetails.DoesNotExist:
            return  Response({"status": "warning", "message": "You don't have any order!", "data":[]}, status=200)

class VendorOneOrderFullDetailsAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        vendorOrderId = pk
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        try:
            vendorOrderObj = VendorOrderDetails.objects.get(vendor=vendorObj, id=vendorOrderId)
            vendorOrderDetailsData = VendorOrderDetailsSerializer(vendorOrderObj, many=False).data

            vendorDetails = vendorOrderDetailsData["vendor"]["user"]
            userAddressDetails = vendorOrderDetailsData["order"]["address"]

            try:
                deliveryExeDetails = vendorOrderDetailsData["order"]["delivery_exe"]["user"]
                deliveryExeDetails.pop("password")
            except:
                deliveryExeDetails = None

            vendorDetails.pop("password")
            userAddressDetails.pop("user")
            

            vendorOrderDetailsData["order_number"] = vendorOrderDetailsData["order"]["order_number"]
            vendorOrderDetailsData.pop("vendor")
            vendorOrderDetailsData.pop("order")

            orderProductObj = OrderProductDetail.objects.filter(product__vendor=vendorObj, order__order_number=vendorOrderDetailsData["order_number"])
            orderProductData = VendorOrderProductDetailSerializer(orderProductObj, many=True).data
            for i in range(len(orderProductData)):
                orderProductData[i].pop("order")

            response = {
                "orderDetails" : vendorOrderDetailsData,
                "vendorDetails" : vendorDetails,
                "userAddressDetails" : userAddressDetails,
                "deliveryExeDetails" : deliveryExeDetails,
                "productDetails" : orderProductData
            }

            return Response({"status": "success", "message": "Order full details fetched success","data": response}, status=200)

        except VendorOrderDetails.DoesNotExist:
            return  Response({"status": "warning", "message": "You don't have any order!", "data":[]}, status=200)

class VendorBusinessSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)

        vendorNoProducts = Product.objects.filter(vendor=vendorObj.id).count()
        vendorOrdersDetailsObj = VendorOrderDetails.objects.filter(vendor=vendorObj)

        # vendorGrossTax = 0.00
        # vendorGrossSell = 0.00
        vendorNoOrders = vendorOrdersDetailsObj.count()

        # orderProductObj = OrderProductDetail.objects.filter(product__vendor=vendorObj, order__payment_status = "Paid")

        # vendorOrdersDetailsData = VendorOrderDetailSerializer(vendorOrdersDetailsObj, many=True).data
        # for oneOrder in vendorOrdersDetailsData:
        #     vendorGrossTax += oneOrder["total_tax"]
        #     vendorGrossSell += oneOrder["total_price"]
        #     vendorNoOrders += 1 

        # vendorGrossProductSell = Product.objects.aggregate(Sum('price')) 
        
        vendorGrossTax = VendorOrderDetails.objects.aggregate(Sum('total_tax'))
        
        vendorGrossProductSell = VendorOrderDetails.objects.aggregate(Sum('total_price')) 
        vendorProductGrossSellAmt = vendorGrossProductSell["total_price__sum"] + vendorGrossTax["total_tax__sum"]

        #vendorProductSerializer = VendorProductGetSerializer(vendorProductObj, many=True)

        response = {
            # "gross_sell" : vendorGrossProductSell,                    # vendorGrossProductSell
            "gross_sell" : vendorProductGrossSellAmt,            # This data can be used when siddarth is work with me that time we update 
            "gross_tax" : vendorGrossTax,
            "total_orders" : vendorNoOrders,
            "total_products" : vendorNoProducts,
            # "tax":vendorGrossTax["total_tax__sum"],
            # "vendorProductGrossSellAmt" : vendorProductGrossSellAmt,
        }
        return Response({
            "status":"success",
            "message" : "Success",
            "data" : response
        }, status=200)


# Sales Report Product Details
class SalesReportProductAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        vendorObj = Vendor.objects.get(user_id=self.request.user.id)
        startDate = self.request.query_params.get("start_date", None)
        endDate = self.request.query_params.get("end_date", None)
        # startDate = '2022-08-29'
        # endDate = '2022-08-30'
        
        orderProductObj = OrderProductDetail.objects.filter(product__vendor=vendorObj, order__payment_status = "Paid", created_at__range=(startDate, endDate))
        orderProductSerializer = OrderProductDetailSerializer(orderProductObj, many=True)

        orderProductList = orderProductSerializer.data

        productList = {}
        for oneProductdata in orderProductList:
            productId = oneProductdata["product"]["id"]
            if oneProductdata["product"]["id"] in productList:
                productList[productId]["price"] = float(oneProductdata["price"])
                productList[productId]["quantity"] += oneProductdata["quantity"]
                productList[productId]["total_price"] += float(oneProductdata["total_price"])
                productList[productId]["tax"] += float(oneProductdata["order"]["tax"])
                productList[productId]["total_price_with_tax"] =  productList[productId]["total_price"] + productList[productId]["tax"]
                productList[productId]["product"] = oneProductdata["product"]
            else:
                productList[productId] = {}
                productList[productId]["price"] = float(oneProductdata["price"])
                productList[productId]["quantity"] = oneProductdata["quantity"]
                productList[productId]["total_price"] = float(oneProductdata["total_price"])
                productList[productId]["tax"] = float(oneProductdata["order"]["tax"])
                productList[productId]["total_price_with_tax"] =  productList[productId]["total_price"] + productList[productId]["tax"]
                productList[productId]["product"] = oneProductdata["product"]

        saleReportList = [] 
        for oneProductId in productList:
            saleReportList.append(productList[oneProductId])

            

        return Response({
            "status": True,
            # "productList": productList,
            "data": saleReportList,
        }, status = 200)