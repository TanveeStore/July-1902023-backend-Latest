from unicodedata import decimal
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from common.models import User
from Wallet.models import MyWallet
from Wallet.serializers import MyWalletSerializer
from rest_framework.views import APIView
from rest_framework import status
import decimal
import random
import razorpay
from django.conf import settings
from orders.views import orderHelperClass
from CartSystem.common.cart_system import get_cart_amt_detail
from orders.models import OrderDetail
from orders.serializers import OrderDetailSerializer
from Notifications.models import Notifications
from common.utils import CommonUtils


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

# Personal
# razorpay_client_personal = razorpay.Client(auth=(settings.RAZORPAY_API_PersonalKEY, settings.RAZORPAY_API_SECRET_PersonalKEY))

# WalletDetailApi
class WalletLastUpdatedTnxApi(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            userObj = self.request.user
            walletObj = MyWallet.objects.filter(user = userObj).first()
            walletSerializer = MyWalletSerializer(walletObj, many=False)

            walletJsonData = walletSerializer.data

            return Response(
                {
                    "status":True,
                    "data": walletJsonData,
                },
                status = status.HTTP_200_OK
            )
        except MyWallet.DoesNotExist:
            return Response(
                {
                    "status":False,
                    "data": [],
                },
                status = status.HTTP_200_OK
            )


# Get All Wallet Transaction History API
class WalletTnxAllHistoryApi(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            userObj = self.request.user
            walletObj = MyWallet.objects.filter(user = userObj, status = "active")
            walletSerializer = MyWalletSerializer(walletObj, many=True)

            walletJsonData = walletSerializer.data

            return Response(
                {
                    "status":True,
                    "data": walletJsonData,
                },
                status = status.HTTP_200_OK
            )
        except MyWallet.DoesNotExist:
            return Response(
                {
                    "status":False,
                    "data": [],
                },
                status = status.HTTP_200_OK
            )


# AddMoneyInWallet
class AddMoneyInWallet(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        userObj = User.objects.get(id=request.user.id)

        userAmount = float(request.data.get("trasactionAmt", 0))
        # order_number = request.data.get("orderNumber", '')
        # razorpay_payment_id = request.data.get('razopayPaymentId', '').
        # razorpay_order_id = request.data.get('razopayOrderId', '')
        # razorpay_signature = request.data.get('razorpay_signature', '')
        # updatedWalletAmt = request.data.get('updatedWalletAmt', False)
        transactionType = request.data.get('transactionType', False)
        walletStatus = request.data.get('status', '')
        
        
        currency = "INR"
        amount = int(userAmount*100)
        # order_number = "WALTNX"+str(random.randint(1001234567, 9000102345))

        

        wallet = MyWallet(user=userObj, trasactionAmt=userAmount, 
                        # orderNumber=order_number, 
                        # razopayPaymentId=razorpay_payment_id, 
                        # razopayOrderId=razorpay_order_id, 
                        # razorpay_signature=razorpay_signature, 
                        transactionType=transactionType,
                        status=walletStatus,
                        )
        wallet.save()

        # Create a Razorpay payment Order
        transactionNumber = wallet.transactionId

        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture="1",
                                                           receipt=transactionNumber))

        responseData = {
            "status": "success",
            "message": "Waiting for razorpay payment",
            "orderAmount": userAmount,
            "data": razorpay_order,
            "transactionNumber": wallet.transactionId,

            # "orderPaymentId": razorpay_order["id"]
        }
        return Response(responseData, status=status.HTTP_200_OK)


# Verify the Payment of Added money in Wallet.
class VerifyWalletMoneyAndActiveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        userObj = self.request.user
        # print(request.data)

        # transactionId is nothing but a receipt no. which is provided by create wallet transaction api response.
        transactionId = request.data.get("transactionId", False)
        razorpay_payment_id = request.data.get('razorpay_payment_id', '')
        razorpay_order_id = request.data.get('razorpay_order_id', '')
        razorpay_signature = request.data.get('razorpay_signature', '')

        try:
            walletObj = MyWallet.objects.get(
                transactionId=transactionId, user=userObj)
            walletDetailsData = MyWalletSerializer(walletObj, many=False).data
            print(walletDetailsData)

            currency = 'INR'
            amount = int(float(walletDetailsData["trasactionAmt"]) * 100)  # Rs.
            print(amount)
            print(type(amount))
            try:

                params_dict = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                }

                print(params_dict)
                
                # verify the payment signature.
                result = razorpay_client.utility.verify_payment_signature(
                    params_dict)
                print(result)
                # verify the payment signature.
                result = razorpay_client.utility.verify_payment_signature(params_dict)

                walletObj.razopayPaymentId = razorpay_payment_id
                walletObj.razopayOrderId = razorpay_order_id
                walletObj.status = "active"
                walletObj.save()


                # if walletObj.status == "active":

                #     textMessage = f'Hello {userObj.first_name}, Your wallet transaction {walletObj.transactionId} has been received. Your current wallet balance is {walletObj.walletBalance}. Please check your wallet balance. see you soon, Team Tanvee Store'
                    
                #      # Customer WalletStatus Notification
                #     userNotificationObj = Notifications.objects.create(user=userObj,
                #                                                 notificationText=textMessage,
                #                                                 notificationType ="transaction",
                #                                                 seenStatus=False)
                #     userNotificationObj.save()
                #     CommonUtils.sendPushNotification(userType="customer", fcmTokens=[userObj.fcm_token], title="Tanvee Notification", msg=textMessage, image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb", dataObject=None)

                
                return Response({"status": "success", "message": "Payment Success!"}, status=200)

            except:
                # if we don't find the required parameters in POST data
                return Response({"status": "warning", "message": "Invalid Inputes!"},
                                status=status.HTTP_400_BAD_REQUEST)
        
        except MyWallet.DoesNotExist:
            return Response({
                "status": "warning",
                "message": "Wallet transaction id not valid"
            }, status=status.HTTP_400_BAD_REQUEST)




# Payment OrderProduct using Wallet  
class CreateOrderDebitWalletBalance(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        userObj = User.objects.get(id=request.user.id)

        payment_method = self.request.data.get("payment_method", False)
        transactionType = self.request.data.get("transactionType", False)
        walletStatus = "active"

        if payment_method != 'wallet':
            return Response({"status": "warning", "message": "Please select Wallet to place order by this api"}, status=406)

        walletObj = MyWallet.objects.filter(user=userObj, status=walletStatus).first()
        walletData = MyWalletSerializer(walletObj, many=False).data
        lastWalletBalance = decimal.Decimal(walletData["walletBalance"])
        print("Last Wallet Balance", lastWalletBalance)
        cartAmtDetails = get_cart_amt_detail(request)
        print("total cart amount", cartAmtDetails["cartAmt"])
        # totalCartAmt = cartAmtDetails["cartAmt"]
        totalCartAmtWithTax = decimal.Decimal((decimal.Decimal(cartAmtDetails["cartAmt"])) + (decimal.Decimal(cartAmtDetails["cartTaxAmt"])))

        if payment_method == 'wallet':
            if lastWalletBalance >= totalCartAmtWithTax:
                orderHelperClassObj = orderHelperClass()
                createOrderHelperResponse = orderHelperClassObj.createOrder(request)
                print(createOrderHelperResponse)

                
                

                orderDetails = createOrderHelperResponse["data"]
                currency = "INR"
                amount = float(orderDetails["grand_total"])
                order_number = orderDetails["order_id"]

                if createOrderHelperResponse["status"] == "success":
                # if createOrderHelperResponse["status"] == "success" and amount<=float(walletData["walletBalance"]):
                    # orderDetails = createOrderHelperResponse["data"]
                    # currency = "INR"
                    # amount = float(orderDetails["grand_total"])
                    # order_number = orderDetails["order_id"]

                    # walletStatus = "active"
                    # transactionType = self.request.data.get("transactionType", False)

                    
                

                    # if amount<=float(walletData["walletBalance"]):

                    # Create a wallet Order
                    wallet_order = MyWallet(user=userObj, trasactionAmt=amount, orderNumber=order_number, 
                                razopayPaymentId='', 
                                razopayOrderId='', 
                                # razorpay_signature=razorpay_signature, 
                                transactionType=transactionType,
                                status=walletStatus,
                                )
                    wallet_order.save()

                    orderObj = OrderDetail.objects.get(order_number=order_number, user=userObj)
                    orderDetailsData = OrderDetailSerializer(orderObj, many=False).data

                    orderObj.payment_status = "Paid"
                    orderObj.order_status = "Order Placed"
                    orderObj.save()

                    walletObj2 = MyWallet.objects.filter(user=userObj, status=walletStatus).first()
                    walletData2 = MyWalletSerializer(walletObj2, many=False).data


                if orderObj.payment_status == "Paid":

                    # Customer Order Sms
                    textMessage = f'Hello {userObj.first_name}, Your order {orderObj.order_number} has been received. Please have patience, your order will be delivered with in 8 business hours. see you soon , Team Tanvee Store' 
                    orderResponse = CommonUtils.SendMobileMessage([userObj.mobile], "order-placed", textMessage)
                    


                    # Customer OrderStatus Notification
                    userNotificationObj = Notifications.objects.create(user=userObj,
                                                                notificationText=textMessage,
                                                                notificationType ="order",
                                                                seenStatus=False)
                    userNotificationObj.save()
                    CommonUtils.sendPushNotification(userType="customer", fcmTokens=[userObj.fcm_token], title="Tanvee Notification", msg=textMessage, image="https://images.unsplash.com/photo-1567473030492-533b30c5494c?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb", dataObject=None)
                
                    responseData = {
                        "status": "success",
                        "message": "Wallet payment done Successfully, Order Placed is Placed",
                        "data": walletData2,
                        "OrderAmount": amount,
                        # "WalletTransAmt": wallet_order.trasactionAmt,
                        # "WalletlastBal": walletData2["walletBalance"],
            
                    }
                    return Response(responseData, status=status.HTTP_200_OK)
                
                else:
                    responseData = {
                        "status": "success",
                        "message": "Wallet payment not Successfully, please try again!!",
                        "OrderAmount": amount,
                        "WalletlastBal": walletData["walletBalance"],
        
                }
                return Response(responseData, status=status.HTTP_200_OK)
    
            
            else:
                responseData = {
                    "status": "success",
                    "message": "Wallet Balance is Less than Order Amount. So try another Payment method!!",
                    # "OrderAmount": amount,
                    "WalletlastBal": walletData["walletBalance"],
    
            }
            return Response(responseData, status=status.HTTP_200_OK)

        else:
            responseData = {
                "status": "warning",
                "message": "Opps!! Something went wrong, try again!!!"
            }
            return Response(createOrderHelperResponse, status=createOrderHelperResponse["status_code"])
