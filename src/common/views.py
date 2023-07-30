from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from common.models import Profile
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.models import User, BankDetails
from common.serializer.user_serializers import (
    AddressSerializer,
    UpdateProfileSerializer,
    UserSerializer,
    UpdateAddressSerializer,
    UserCompleteSerializer,
    UserProfileBasicSerializerUpdate,
    ForgotPasswordSerializer,
    SetNewPasswordSerializer,
    BankDetailsSerializer,
)
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics
from django.utils.encoding import force_text
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import random
from django.conf import settings
from django.contrib import auth
# Create your views here.


class UserProfileDetailAPIView(APIView):
    #permission_classes = (IsAuthenticated)

    def get_object(self, pk):
        profile = get_object_or_404(Profile, pk=pk)
        return profile

    def put(self, request, pk, format=None):
        params = request.query_params if len(
            request.data) == 0 else request.data
        profile = self.get_object(pk)
        address_obj = profile.address

        serializer = UserSerializer(
            data=params, instance=profile.user)
        address_serializer = UpdateAddressSerializer(
            data=params, instance=address_obj)
        profile_serializer = UpdateProfileSerializer(
            data=params, instance=profile)
        data = {}
        if not serializer.is_valid():
            data["contact_errors"] = serializer.errors
        if not address_serializer.is_valid():
            data["address_errors"] = (address_serializer.errors,)
        if not profile_serializer.is_valid():
            data["profile_errors"] = (profile_serializer.errors,)
        if data:
            data["error"] = True
            return Response(
                data,
                status=status.HTTP_400_BAD_REQUEST,
            )
        if serializer.is_valid():
            address_obj = address_serializer.save()
            user = serializer.save()
            user.username = user.first_name
            user.save()
            profile = profile_serializer.save()
            return Response(
                {"error": False, "message": "User Updated Successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


# User Profile Get And Update
class UserProfileBasicAPIview(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        jsonData = UserCompleteSerializer(userObj)
        vendorProfile = jsonData.data
        return Response({"status": "success", "message": "Basic Profile fetched successfully",
                         "data": vendorProfile}, status=200)

    def delete(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        userObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        # userObj=User.objects.get(id=self.request.user.id)
        # basicProfileSerializer = UserProfileBasicSerializerUpdate(userObj, data=request.data, partial=True)

        # if basicProfileSerializer.is_valid():
        #     basicProfileSerializer.save()
        #     return Response({"status": "success","message":"Basic Profile updated successfully"},status=200)
        # else:
        #     return Response({"status": "warning","message":"Invalid inputes","errors":basicProfileSerializer.errors},status=400)

        userMobile = request.data.get("mobile", None)
        userEmail = request.data.get("email", None)
        isEmailExist = False
        isMobileExist = False

        if userMobile is not None:
            if User.objects.filter(mobile=userMobile).count() > 0:
                isMobileExist = True
        if userEmail is not None:
            if User.objects.filter(email=userEmail).count() > 0:
                isEmailExist = True

        if isMobileExist != True and isEmailExist != True:
            userObj = User.objects.get(id=self.request.user.id)
            basicProfileSerializer = UserProfileBasicSerializerUpdate(
                userObj, data=request.data, partial=True)

            if basicProfileSerializer.is_valid():
                basicProfileSerializer.save()
                return Response({"status": "success", "message": "Basic Profile updated successfully"}, status=200)
            else:
                return Response({"status": "warning", "message": "Invalid inputes", "errors": basicProfileSerializer.errors}, status=400)
        else:
            if isMobileExist is True:
                return Response({"status": "warning", "message": "Mobile already exists try to use a different mobile"}, status=200)
            else:
                return Response({"status": "warning", "message": "Email already exists try to use a different email"}, status=200)


class FcmTokenApiView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        userId = request.user.id
        fcm_token = request.data.get('fcm_token', None)
        if fcm_token is None:
            return Response({"status": "warning", "message": "Please provide FCM token!"}, status=200)


        User.objects.filter(id = userId).update(fcm_token = fcm_token)
        # userObj = User.objects.get(id=userId)
        # User(userObj, fcm_token=fcm_token)
        # User.save()

        return Response({"status": "success", "message": "FCM token updated successfully"}, status=200)



# Forgot Password APIView
class ForgotPasswordView(APIView):

    def post(self, request, format=None):
        params = request.query_params if len(
            request.data) == 0 else request.data
        email = request.data.get('email', '')
        userObj = User.objects.filter(email=email).first()
        serializer = ForgotPasswordSerializer(data=params)

        if serializer.is_valid():
            user = get_object_or_404(User, email=params.get("email"))
            if not user.is_active:
                return Response(
                    {"error": True, "errors": "Please activate account to proceed."},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )
            protocol = self.request.scheme

            context = {}
            context["email"] = userObj.email
            domain="tanveestore.com"
            context["url"] = protocol + "://" + domain
            context["uid"] = (urlsafe_base64_encode(force_bytes(user.pk)),)
            context["token"] = default_token_generator.make_token(user)
            context["token"] = context["token"]
            context["complete_url"] = context[
                "url"
            ] + "/password-reset-complete/{uidb64}/{token}/".format(
                uidb64=context["uid"][0], token=context["token"]
            )

            # # Send Reset link on Email
            # mailSubject = "Welcome to Tanvee!!!"
            # mailMessage = "Hello " + userObj.first_name + "! Thanks for joining with us. Your email: " + userObj.email + " . Please Use This link to reset your password.Thanks Again! Happy Business! Tanvee Store Team." + context["complete_url"]
            # mailFrom = 'developer.akash09@gmail.com'
            # mailTo = [email]
            # send_mail(mailSubject, mailMessage, mailFrom, mailTo, fail_silently=False)


            # send_email_to_reset_password(
            #      user.email, protocol=protocol, domain="tanveestore.com"
            # )
            data = {
                "error": False,
                "uid": context["uid"],
                "token": context["token"],
                "message": "please reset password"
                 
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = {"error": True, "errors": serializer.errors}
            response_status = status.HTTP_400_BAD_REQUEST
        return Response(data, status=response_status)



# SetNew Password
class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password reset success'}, status=status.HTTP_200_OK)


# Forgot Password with sending OTP through Email.
class ForgotPasswordOtpEmail(APIView):

    def post(self, request, *args, **kwargs):

        email = request.data.get('email', False)
        
        try:
            otp = str(random.randint(1000, 9999))
            userObj = User.objects.get(email=email)
            try:
                profile = Profile.objects.get(user_id=userObj.id)
                profile.otp = otp
                profile.save()
            except Profile.DoesNotExist:
                return Response({"status": "warning", "message": "Opps! Profile doesn't Exist, please try again with valid email!!"}, status=200)
            
            # Send Otp on Email
            mailSubject = "Welcome to Tanvee!!!"
            mailMessage = "Hello " + userObj.first_name + " " + userObj.last_name +  "! Thanks for joining with us. Your email: " + email + ". This is Your Otp for reset Password: " + otp + " . Please reset the password and Enjoy Our Service. Thanks Again! Happy Business! Tanvee Team."
            mailFrom = settings.EMAIL_HOST_USER
            mailTo = [email]
            otpResponse = send_mail(mailSubject, mailMessage, mailFrom, mailTo, fail_silently=False)

            ''' # Get the SuperUser Details by is_superuser=True 
            superusers = User.objects.get(is_superuser=True)

            # send Email to SuperUser 
                superuser_mailMessage = "Hello " + superusers.first_name + " " + superusers.last_name + " This " + userObj.role + " " + userObj.first_name + " "+ userObj.last_name + " | " + userObj.mobile + " has requested a password change on this " +  userObj.email + ". OTP has been sent to him/her! Tanvee Team "
                mailtoSuperUser = [superusers.email]
                send_mail(mailSubject,superuser_mailMessage,mailFrom,mailtoSuperUser, fail_silently=False)
            '''

            if otpResponse == True:
                return Response({"status": "success", "message": "Otp send on your registerd email successfully"}, status=200)
            else:
                return Response({"status": "warning", "message": "Opps! Otp send fail, try again!!"}, status=200)

        except User.DoesNotExist:
            return Response({"status": "warning", "message": "email is Not Valid"}, status=status.HTTP_200_OK)


# Reset Password with OTP.
class ResetPasswordOTP(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        email = request.data.get('email', False)
        otp = request.data.get('otp', False)
        new_password = request.data.get('new_password', False)
        confirm_password = request.data.get('confirm_password', False)
        userObj = User.objects.get(email=email)
        print(userObj.id)
        # profile = Profile.objects.get(otp=otp)
        profile = Profile.objects.get(user_id=userObj.id)
        # profile = Profile.objects.filter(user_id = userObj.id)

        try:
            user = auth.authenticate(
                request, email=request.data["email"], otp=request.data["otp"])
        except (User.DoesNotExist, Exception):
            return Response({"status": False, "data": {"message": "Invalid credentials"}},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            if profile.user.is_active:
                # Check if otp is valid
                if profile.otp == otp:
                    if len(data.get('new_password')) < 6:
                        return Response({"error": True, "message": "Password must be at least 6 characters long!"}
                            )

                    if data.get('new_password') != data.get('confirm_password'):
                        # raise serializers.ValidationError(
                        #     "New_password and confirm_password did not match.")
                        return Response({"error":True, "message": "New_password and confirm_password did not match"})

                    profile.user.set_password(data['new_password'])
                    profile.user.save()
                else:
                    context = {'error':True, 'message': 'You Enter Wrong OTP'
                        }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
                
                # Get the SuperUser Details by is_superuser=True 
                superusers = User.objects.get(is_superuser=True)

                # send Email to SuperUser 
                superuser_mailMessage = "Hello " + superusers.first_name + " " + superusers.last_name + " This " + userObj.role + " " + userObj.first_name + " "+ userObj.last_name + " has change the password on this " +  userObj.email + ".| Tanvee Team "
                mailSubject = "Welcome to Tanvee!!!"
                mailFrom = settings.EMAIL_HOST_USER
                mailtoSuperUser = [superusers.email]
                send_mail(mailSubject,superuser_mailMessage,mailFrom,mailtoSuperUser, fail_silently=False)
                

                return Response({'status':"success", 'message': " password reset successfully"}, status=status.HTTP_200_OK)
            else:
                message = {
                'detail': 'Something went wrong'}
                return Response(message, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            
             return Response({"status": "warning", "message": " Profile doesn't exist"}, status=status.HTTP_200_OK)


# Customer Bank Details API (get, post)
class CustomerBankDetailsAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        
        try:
            customerBankDetailObj = BankDetails.objects.get(user_id=self.request.user.id)
            jsonData = BankDetailsSerializer(customerBankDetailObj, many=False)
            customerBankDetails = jsonData.data
            return Response({"status": "success","message":"Bank details fetched successfully","data":customerBankDetails},status=200)
        
        except BankDetails.DoesNotExist:
            return Response({"status": "warning", "message":"You don't have any Bank details", "data":[]},status=200)

    
    def post(self, request):
        user_id = self.request.user.id
        regData=request.data
        regData["user"] = user_id
        regData["is_default"] = True
        try:
            customerBankDetailObj = BankDetails.objects.get(user_id=self.request.user.id)
            customerBankSerializer = BankDetailsSerializer(customerBankDetailObj, data=regData, partial=True)
            if customerBankSerializer.is_valid():
                customerBankSerializer.save()
                return Response({"status": "success","message": "Bank details updated successfully"}, status=200)
            else:
                return Response({"status": "warning","message": "Invalid inputes","errors": customerBankSerializer.errors}, status=400)
        except BankDetails.DoesNotExist:
            customerBankSerializer = BankDetailsSerializer(data=regData)
            if customerBankSerializer.is_valid():
                customerBankSerializer.save()
                return Response({"status": "success","message": "Bank added successfully"}, status=201)
            else:
                return Response({"status": "warning","message": "Invalid inputes", "errors": customerBankSerializer.errors}, status=400)
