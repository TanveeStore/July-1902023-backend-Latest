from django.urls import path, include, re_path
from common.api.user import (
    Register,
    ValidateOTP,
    LoginOTP,
    LoginApiView,
    LogoutApiView,
    UserAccountLogoutApiView,
    ResendOtp,
)
from common import views
from common.social.social_media_apis import GoogleLogin, FacebookLogin
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework import routers

router = routers.DefaultRouter()

app_name = "common"

router.register("google-login", GoogleLogin, "user-google-login"),
router.register("facebook-login", FacebookLogin,
                "user-facebook-login"),

urlpatterns = [
    # path('sendotp/', SendPhoneOTP.as_view()),
    # path('validatemobileotp/', ValidateMobileOTP.as_view()),
    path('validateotp/', ValidateOTP.as_view()),
    path('register/', Register.as_view()),
    path('login/', LoginApiView.as_view()),
    path('fcm-token/', views.FcmTokenApiView.as_view()),
    path('login-otp/', LoginOTP.as_view()),
    # This is Working but in use bcoz some error
    path('logout/', LogoutApiView.as_view(), name='auth_logout'),

    path('log-out/', UserAccountLogoutApiView.as_view()),     # This APi is Logout

    # Resend Otp
    path('resend-otp/', ResendOtp.as_view(), name='resend_otp'),

    path('customer/profile/<int:pk>', views.UserProfileDetailAPIView.as_view()),
    path('customer/my-details/', views.UserProfileBasicAPIview.as_view()),
    # path('customer/my-details/', views.UserProfileBasicAPIview.as_view()),

    # Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Forgot Password
    path("forgot-password/", views.ForgotPasswordView.as_view()),

    # Reset Password
    path('password-reset-complete/', views.SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),


    # Forgot Password with email-otp
    path("forgot-password-send-otp/", views.ForgotPasswordOtpEmail.as_view()),

    # Forgot Password with email-otp
    path("reset-password-with-otp/", views.ResetPasswordOTP.as_view()),

    # Customer-Bank-Details
    path("customer-bank-details/", views.CustomerBankDetailsAPI.as_view()),
]

urlpatterns += router.urls
