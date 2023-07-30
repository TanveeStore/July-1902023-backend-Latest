from django.shortcuts import render, redirect
from django.http import HttpResponse
from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import api_view
from django.contrib.auth import login
from common.helper import CommonHelper
from common.otp_utils import phone_validator, password_generator, otp_generator
from common.models import User, Profile, Address
from common.serializer.user_serializers import (
    UserCompleteSerializer,
    LogoutSerializer,
    UserLogoutSerializer,
    UserAccountLogoutSerializer,
    ResentOtpSerializer,
    LoginWithMobileUserSerializer)
from django.shortcuts import get_object_or_404
from django.db.models import Q
import requests
import random
import re
import decimal
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.mail import send_mail
from Notifications.send_sms import sendsms
from django.contrib import auth
# from validate_email import validate_email
from email_validator import validate_email, EmailNotValidError
from django.conf import settings
from Wallet.models import MyWallet
from common.utils import CommonUtils

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def send_otp(mobile):
    """
    This is an helper function to send otp to session stored phones or
    passed mobile number as argument.
    """

    if mobile:

        key = otp_generator()
        mobile = str(mobile)
        otp_key = str(key)

        # link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=fc9e5177-b3e7-11e8-a895-0200cd936042&to={phone}&from=wisfrg&templatename=wisfrags&var1={otp_key}'

        # result = requests.get(link, verify=False)

        return otp_key
    else:
        return False


"""def send_otp_forgot(mobile):
    if mobile:
        key = otp_generator()
        mobile = str(mobile)
        otp_key = str(key)
        user = get_object_or_404(User, mobile__iexact=mobile)
        if user.first_name:
            name = first_name
        else:
            name = mobile

        # link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=fc9e5177-b3e7-11e8-a895-0200cd936042&to={phone}&from=wisfgs&templatename=Wisfrags&var1={name}&var2={otp_key}'

        # result = requests.get(link, verify=False)
        # print(result)

        return otp_key
    else:
        return False
"""

"""class ValidatePhoneSendOTP(APIView):
    '''
    This class view takes phone number and if it doesn't exists already then it sends otp for
    first coming phone numbers'''

    def post(self, request, *args, **kwargs):
        mobile_number = request.data.get('mobile')
        if mobile_number:
            mobile = str(mobile_number)
            user = User.objects.filter(mobile__iexact=mobile)
            if user.exists():
                return Response({'status': False, 'detail': 'Mobile Number already exists'})
                # logic to send the otp and store the phone number and that otp in table.
            else:
                otp = send_otp(mobile)
                print(mobile, otp)
                if otp:
                    otp = str(otp)
                    count = 0
                    old = MobileOTP.objects.filter(mobile__iexact=mobile)
                    if old.exists():
                        count = old.first().count
                        old.first().count = count + 1
                        old.first().save()

                    else:
                        count = count + 1

                        MobileOTP.objects.create(
                            mobile=mobile,
                            otp=otp,
                            count=count

                        )
                    if count > 7:
                        return Response({
                            'status': False,
                            'detail': 'Maximum otp limits reached. Kindly support our customer care or try with different number'
                        })


                else:
                    return Response({
                        'status': 'False', 'detail': "OTP sending error. Please try after some time."
                    })

                return Response({
                    'status': True, 'detail': 'Otp has been sent successfully.'
                })
        else:
            return Response({
                'status': 'False', 'detail': "I haven't received any mobile number. Please do a POST request."
            })


class ValidateOTP(APIView):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to set the password

    '''

    def post(self, request, *args, **kwargs):
        mobile = request.data.get('mobile', False)
        otp_sent = request.data.get('otp', False)

        if mobile and otp_sent:
            old = MobileOTP.objects.filter(mobile__iexact=mobile)
            if old.exists():
                old = old.first()
                otp = old.otp
                if str(otp) == str(otp_sent):
                    old.logged = True
                    old.save()

                    return Response({
                        'status': True,
                        'detail': 'OTP matched, kindly proceed to save password'
                    })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP incorrect, please try again'
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'Mobile not recognised. Kindly request a new otp with this number'
                })


        else:
            return Response({
                'status': 'False',
                'detail': 'Either Mobile or otp was not recieved in Post request'
            })
"""


class Register(APIView):
    '''Takes mobile and otp and creates a new user only if otp was verified and mobile number is new'''

    def post(self, request, *args, **kwargs):

        # password = request.data.get('password', False)
        email = request.data.get('email', False)
        mobile = request.data.get('mobile', False)
        first_name = request.data.get('first_name', False)
        last_name = request.data.get('last_name', False)
        # username = request.data.get('username', False)

        check_email = User.objects.filter(email=email).first()
        check_mobile = User.objects.filter(mobile=mobile).first()

        '''if not validate_email(
                email_address=email,
                check_format=True,
                check_blacklist=True,
                check_dns=True,
                dns_timeout=10,
                check_smtp=True,
                smtp_timeout=10,
                smtp_helo_host='my.host.name',
                smtp_from_address='my@from.addr.ess',
                smtp_skip_tls=False,
                smtp_tls_context=None,
                smtp_debug=False
        ):

            return Response("Email is not valid", status=status.HTTP_400_BAD_REQUEST)'''

        try:
            # Validate & take the normalized form of the email
            # address for all logic beyond this point (especially
            # before going to a database query where equality
            # does not take into account normalization).
            email = validate_email(email).email
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            return Response("Email is not Valid!!", status=status.HTTP_400_BAD_REQUEST)

        '''def check(email):

            # pass the regular expression
            # and the string into the fullmatch() method
            if (re.fullmatch(regex, email)):
                print("Valid Email")

            else:
                print("Invalid Email")'''
        errors = {}
        if not email:
            errors['email'] = ['This email is required']
        if len(email) < 10:
            errors['email'] = ['Email must be 10 char long or more']
        if (not mobile):
            errors['mobile'] = ['This email is required']
        if len(mobile) < 10:
            errors['mobile'] = ['Mobile Number must be 10 digit or more']
        if len(mobile) > 13:
            errors['mobile'] = ['Mobile Number must be less than 13 digit']
        if not first_name:
            errors['first_name'] = ['This email is required']
        if len(first_name) <= 2:
            errors['first_name'] = ['First Name must be 2 char long or more']
        if not last_name:
            errors['last_name'] = ['This email is required']
        if len(last_name) <= 2:
            errors['first_name'] = ['Last Name must be 2 char long or more']
        if errors:
            return Response({'error': True, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        if check_mobile:
            context = {'message': "Hello!" + " " + mobile +
                       " " + "This Mobile number already exists"}
            return Response({"status": False, "context": context}, status=status.HTTP_200_OK)

        elif check_email:
            context = {'message': "Hello!" + " " +
                       email + " " + "This Email already exists"}
            return Response({"status": False, "context": context}, status=status.HTTP_200_OK)

        user = User(email=email, first_name=first_name,
                    last_name=last_name, mobile=mobile)
        user.save()
        # key = otp_generator()
        otp = str(random.randint(2468, 9999))
        # otp_key = str(key)
        profile = Profile(user=user, otp=otp)
        print(profile)
        profile.save()

        textMessage = f'Welcome to Tanvee Store Family , your one time verification code is {otp}'
        otpResponse = CommonUtils.SendMobileMessage(
            [mobile], "otp", textMessage)
        if otpResponse == True:
            return Response({"status": "success", "message": "Otp sent to your mobile number successfully"}, status=200)
        else:
            return Response({"status": "warning", "message": "Opps! Otp send fail, Try again!!"}, status=200)

        # return Response({"status": "success", "message": "Otp send your Register Mobile Number successfully, OTP:"+otp}, status=200)

        # send_otp(mobile, otp)

        # Send Otp on Email
        # mailSubject = "Welcome to Tanvee!!!"
        # mailMessage = "Hello " + first_name + "! Thanks for joining with us. Your email: " + email + " Your Register Mobile Number is : " + mobile + " and your Otp : " + otp + " . Please do login in your account and Enjoy Our Service. Thanks Again! Happy Business! Tanvee Team."
        # mailFrom = "dev.rachhel@gmail.com"
        # mailTo = [email]
        # send_mail(mailSubject, mailMessage, mailFrom, mailTo, fail_silently=False)

        # Send Otp on Mobile
        # sendsms()

        # request.session['mobile'] = mobile
        # return Response({"status": "success", "message": "Otp send your Register Mobile Number sucessfully, OTP: "+otp}, status=200)


'''
        if mobile and password:
            mobile = str(mobile)
            user = User.objects.filter(mobile__iexact=mobile)
            if user.exists():
                return Response({'status': False,
                                 'detail': 'Mobile Number already have account associated. Kindly try forgot password'})
            else:
                old = MobileOTP.objects.filter(mobile__iexact=mobile)
                if old.exists():
                    old = old.first()
                    if old.logged:
                        Temp_data = {'mobile': mobile, 'password': password}

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()

                        old.delete()
                        return Response({
                            'status': True,
                            'detail': 'Congrats, user has been created successfully.'
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': 'Your otp was not verified earlier. Please go back and verify otp'

                        })
                else:
                    return Response({
                        'status': False,
                        'detail': 'Mobile number not recognised. Kindly request a new otp with this number'
                    })


        else:
            return Response({
                'status': 'False',
                'detail': 'Either mobile or password was not recieved in Post request'
            })
'''


'''def otp(request):
    mobile = request.session['mobile']
    context = {'mobile': mobile}
    print(context)
    if request.method == 'POST':
        otp = request.POST.get('otp')
        print(otp)
        profile = Profile.objects.filter(user__mobile=mobile).first()
        # check_user = User.objects.filter(mobile=mobile).first()

        if otp == profile.otp:
            return HttpResponse("OTP matched, kindly proceed to login")
            # return redirect('cart')
        else:
            print('Wrong')

            context = {'message': 'Wrong OTP',
                'class': 'danger', 'mobile': mobile}
            return render(request, 'otp.html', context)

    return render(request, 'otp.html', context)'''


#
class ValidateOTP(APIView):
    '''
     This class view takes phone number and it sends otp for
     first coming phone numbers
    '''

    def post(self, request, *args, **kwargs):
        mobile = request.data.get('mobile', False)
        context = {'mobile': mobile}
        print(context)
        otp = request.data.get('otp', False)
        print(otp)
        profile = Profile.objects.filter(user__mobile=mobile).first()

        user = auth.authenticate(
            profile__user__mobile=mobile, profile__otp=otp)

        errors = {}
        if not mobile:
            errors['mobile'] = [
                'Mobile number is required!!. Please Enter Mobile Number']
        elif len(mobile) < 10:
            errors['mobile'] = ['Mobile Number must be 10 digit or more']
        elif len(mobile) > 13:
            errors['mobile'] = ['Mobile Number must be less than 13 digit']
        elif not profile:
            errors['profile'] = ["This Mobile number doesn't exists"]

        if errors:
            return Response({'error': True, 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        if otp == profile.otp:
            '''return HttpResponse("OTP matched, Your Otp is Validate")
            # return redirect('cart')'''
            refresh = RefreshToken.for_user(profile.user)

            walletObj = MyWallet.objects.filter(user=profile.user).exists()
            if walletObj:
                print("wallet is already exists")
            else:
                wallet = MyWallet(user=profile.user, walletBalance=decimal.Decimal(0.00))
                wallet.status = "active"
                wallet.save()
                print(wallet)

            print(refresh)
        else:
            print('Wrong')

            context = {'message': 'Wrong OTP',
                       'class': 'danger', 'mobile': mobile}
            return Response({"status": False,  "context": context}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "status": True,
            "detail": 'Otp has been matched successfully. Please Validate your Account',
            # 'tokens': user.tokens,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
            status=status.HTTP_200_OK
        )

        # if not profile:
        #     context = {'message': "Hello!" + " " + mobile + " " + "This Mobile number doesn't exists"}
        #     return Response({"status": False, "context": context}, status=status.HTTP_200_OK)


# class ValidateMobileOTP(APIView):
#     '''
#     This class view takes phone number and it sends otp for
#     first coming phone numbers'''
#
#     def post(self, request, *args, **kwargs):
#         mobile = request.session['mobile']
#         otp = request.data.get('otp', False)
#         profile = Profile.objects.filter(user__mobile=mobile).first()
#
#         if otp == profile.otp:
#             # otp = str(otp)
#             # otp = profile.otp
#             count = 0
#             old = Profile.objects.filter(user__mobile=mobile)
#             if old.exists():
#                 count = old.first().count
#                 old.first().count = count + 1
#                 old.first().save()
#
#             else:
#                 count = count + 1
#
#                 Profile.objects.create(
#
#                     otp=otp,
#                     count=count
#
#                 )
#             if count > 10:
#                 return Response({
#                     'status': False,
#                     'detail': 'Maximum otp limits reached. Kindly support our customer care or try with different number'
#                 })
#
#
#         else:
#             return Response({
#                 'status': 'False', 'detail': "OTP sending error. Please try after some time."
#             })
#
#         return Response({
#             'status': True, 'detail': 'Otp has been matched successfully.'
#         })


class LoginApiView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = LoginWithMobileUserSerializer(data=request.data)
        if serializer.is_valid():
            mobile = request.data.get('mobile', False)

            try:
                user = User.objects.get(mobile=mobile)
                # user = auth.authenticate(request, mobile=request.data["mobile"])

                # profile = Profile.objects.filter(user__mobile=mobile).first()
                # user = User.objects.filter(email=self.email).first
                user_id = user.id
                user_email = user.email
                otp = str(random.randint(1234, 9999))
                try:
                    profile = Profile.objects.get(user_id=user_id)
                    profile.otp = otp
                    profile.save()
                except Profile.DoesNotExist:
                    Profile.objects.create(
                        user_id=user_id, address_id='', role='user', otp=otp)
                # profile.otp = otp
                # profile.save()
                # send_otp(mobile, otp)
                recipients = []
                recipients.append(user_email)

                textMessage = f'Welcome to Tanvee Store Family , your one time verification code is {otp}'
                otpResponse = CommonUtils.SendMobileMessage(
                    [mobile], "otp", textMessage)
                if otpResponse == True:
                    return Response({"status": "success", "message": "Otp send your Register Mobile Number successfully"}, status=200)
                else:
                    return Response({"status": "warning", "message": "Opps! Otp send fail, Try again!!"}, status=200)

                    # mailSubject = "Welcome to Tanvee!!!"
                    # mailMessage = "! Thanks for joining with us. Your Register Mobile Number is : " + mobile + " and your Otp : " + otp + " . Please do login in your account and Enjoy Our Service. Thanks Again! Happy Business! Tanvee Team."
                    # mailFrom = "dev.rachhel@gmail.com"
                    # to=recipients
                    # send_mail(mailSubject, mailMessage, mailFrom, to, fail_silently=False)

                    # request.session['mobile'] = mobile

                # return Response({"status": "success", "message": "Otp send your Register Mobile Number successfully, OTP:"+otp}, status=200)

            except User.DoesNotExist:
                return Response({"status": "warning", "message": "This Mobile Number doesn't match!!. Please Enter Valid register Number!!"}, status=204)
                # return Response({"status": False, "data": {"message": "Invalid credentials"}},status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"status": "warning", "message": "Invalid inputes!", "errors": serializer.errors}, status=400)


class LoginOTP(APIView):

    def post(self, request, *args, **kwargs):
        """mobile = request.data.get('mobile', False)
        context = {'mobile': mobile}
        print(context)
        otp = request.data.get('otp', False)
        profile = Profile.objects.filter(user__mobile=mobile).first()
        data = profile.otp
        print(data)
        if otp == profile.otp:"""

        mobile = request.data.get('mobile', False)
        context = {'mobile': mobile}
        print(mobile)
        # print(context)
        otp = request.data.get('otp', False)
        print(otp)
        profile = Profile.objects.filter(user__mobile=mobile).first()
        data = profile.otp
        print(data)
        # user = auth.authenticate(mobile=mobile, otp=otp)

        try:
            check = User.objects.get(mobile=mobile)
            user = auth.authenticate(
                request, mobile=request.data["mobile"], otp=request.data["otp"])
        except (User.DoesNotExist, Exception):
            return Response({"status": False, "data": {"message": "Invalid credentials"}},
                            status=status.HTTP_404_NOT_FOUND)

        if otp == profile.otp:
            # user = User.objects.get(id=profile.user.id)
            # login(request, user)
            refresh = RefreshToken.for_user(profile.user)

            walletObj = MyWallet.objects.filter(user=profile.user).exists()
            if walletObj:
                print("wallet is already exists")
            else:
                wallet = MyWallet(user=profile.user, walletBalance=decimal.Decimal(0.00))
                wallet.status = "active"
                wallet.save()
                print(wallet)

            '''return {
                'email': user.email,
                'mobile': user.mobile,
                'tokens': user.tokens
            }'''

            # return redirect('cart')

        else:
            context = {'message': 'You Enter Wrong OTP',
                       'class': 'danger', 'mobile': mobile}
            return Response(
                {'status': True, 'context': context},
                status=status.HTTP_400_BAD_REQUEST
            )
            # return render(request, 'login_otp.html', context)

        return Response(
            {
                "error": False,
                "message": "User login Successfully.",
                # 'tokens': user.tokens,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_200_OK

        )


# Logout Api
class LogoutApiView(generics.GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # print(serializer.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            resopnseData = {
                "error": False,
                "logout": True,
                "data": "You are Logout Sucessfully!"
            }
            return Response(
                resopnseData,
                status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Bad Request",
                             "message": "Invalid refresh token",
                             },
                            status=status.HTTP_404_NOT_FOUND)


# Logout
# class LogoutUser(mixins.CreateModelMixin, viewsets.GenericViewSet):
#     serializer_class = LogoutSerializer
#     permission_classes = [IsAuthenticated]
#
#     def create(self, request):
#         try:
#
#             refresh_token = request.data["refresh_token"]
#             token = RefreshToken(refresh_token)
#             print(token)
#             token.blacklist()
#             return Response({"logout": True}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"message": "Refresh Token is required"}, status=status.HTTP_404_NOT_FOUND)


# Logout
class UserAccountLogoutApiView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserLogoutSerializer

    def post(self, request):
        try:

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            resopnseData = {
                "error": False,
                "logout": True,
                "data": "You are Logout Sucessfully!"
            }
            # responseData = "You Logout Sucessfully"
            return Response({"data": resopnseData}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response("You not perform this action please try again!!.", status=status.HTTP_400_BAD_REQUEST)


'''class LoginUser(APIView):
    serializer_class = user_serializers.LoginSerializer
    permission_classes = [AllowAny]



    @csrf_exempt
    def create(self, request):
        mobile = request.data.get('mobile', False)

        profile = Profile.objects.filter(user__mobile=mobile).first()
        # serializer = user_serializers.LoginSerializer(data=request.data)
        if profile.is_valid():
            mobile = mobile

            try:
                check = User.objects.get(mobile=mobile)
                user = authenticate(
                    request, mobile=request.data["mobile"])
            except (User.DoesNotExist, Exception):
                return Response({"status": False, "data": {"message": "Invalid credentials"}}, status=status.HTTP_404_NOT_FOUND)
            if user:
                token = RefreshToken.for_user(user)
                data = {
                    "userId": user.id,
                    "email": user.email,
                    "isVerified": user.is_verified,
                    "accessToken": str(token.access_token),
                    "refreshToken": str(token)
                }
                return Response({"status": True, "data": data}, status=status.HTTP_200_OK)
            else:
                return Response({"status": False, "data": {"message": "Invalid credentials"}}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response({"status": False, "data": {"message": "Invalid credentials", "error": serializer.errors}}, status=status.HTTP_406_NOT_ACCEPTABLE)
'''


class ResendOtp(APIView):
    def post(self, request):

        mobile = request.data.get('mobile', False)

        try:
            otp = random.randint(1000, 9999)
            userObj = User.objects.get(mobile=mobile)
            # user = User.objects.filter(mobile=userObj.mobile)
            try:
                profile = Profile.objects.get(user_id=userObj.id)
                profile.otp = otp
                profile.save()
            except Profile.DoesNotExist:
                return Response({"status": "warning", "message": "Opps! Otp send fail, try again!!"}, status=200)

            textMessage = f'Welcome to Tanvee Store Family , your one time verification code is {otp}'
            otpResponse = CommonUtils.SendMobileMessage(
                [mobile], "otp", textMessage)
            if otpResponse == True:
                return Response({"status": "success", "message": "Otp resend your mobile number success"}, status=200)
            else:
                return Response({"status": "warning", "message": "Opps! Otp send fail, try again!!"}, status=200)

        except User.DoesNotExist:
            return Response({"status": "warning", "message": "Mobile Number is Not Valid"}, status=status.HTTP_200_OK)
