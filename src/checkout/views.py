# from django.shortcuts import render
# import razorpay
# from django.conf import settings
# from django.http import HttpResponse
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from orders.models import OrderDetail, OrderProductDetail
# from orders.serializers import OrderDetailSerializer
# import decimal
# from django.shortcuts import render,get_object_or_404


# # client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))
# # client.order.payment(orderId)

# # authorize razorpay client with API Keys.
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))


# # Create Order for payment process
# # class CreateOrder(APIView):
# #
# #     def post(self, request, *args, **kwargs):
# #         order_id = request.data.get('order_number', False)
# #         order = get_object_or_404(OrderDetail, order_number=order_id)
# #         #amount = int(order.get_total_cost() * 100)
# #         amount = int(order.grand_total * 100)
# #         amount_inr = amount // 100
# #         print(order_id)
# #         print("Type amount ", amount)
# #         print("Type amount ", type(amount))
# #         print("Order is -> ", order)
# #         return Response(
# #                       {'order_id': order_id, 'public_key': settings.RAZORPAY_API_KEY, 'amount': amount_inr,
# #                        'amountorig': amount})

# # # Checkout With Payment
# # class CheckoutApiView(APIView):
# #
# #     # permission_classes = [IsAuthenticated]
# #
# #     def post(self, request, *args, **kwargs):
# #         order_id = request.session.get('order_number')
# #         order = get_object_or_404(OrderDetail, id=order_id)
# #         print("Payment", order)
# #         order.save()
# #         orderitem = get_object_or_404(OrderProductDetail, order=order)

# class RazorPayCreatePaymentAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         print(request.data)

#         userObj = self.request.user

#         currency = 'INR'
#         # amount = 200 * 100  # Rs. 200

#         order = OrderDetail.objects.filter(user=userObj).first()
#         orderSerializerData = OrderDetailSerializer(order, many=False).data
#         if order:
#             if order.payment_method == "Razorpay":
#                 totalAmount = orderSerializerData["grand_total"]
#                 print(totalAmount)
#                 amount = int(decimal.Decimal(totalAmount)*100)
#                 print(amount)
#                 # Create a Razorpay Order
#                 razorpay_order = razorpay_client.order.create(dict(amount=amount,
#                                                         currency=currency,
#                                                         payment_capture="1"))
#                 print(razorpay_order)
#             return Response({"data": orderSerializerData},
#                         status=status.HTTP_200_OK)
#         else:
#             return Response({"responseData": "Order doesnt place"})

#         return Response({"responseData": " Payment is successfully done!!"}, status=status.HTTP_200_OK)

# class RazorPayVerifyPaymentAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         #print(request.data)

#         userObj = self.request.user
#         order = OrderDetail.objects.get(user=userObj, payment_method="razorpay").first()

#         currency = 'INR'
#         #amount = 200 * 100  # Rs. 200
#         amount = order.grand_total * 100
#         print(type(amount))
#         print(amount)

#         try:
#             # get the required parameters from post request.
#             payment_id = request.data.get('razorpay_payment_id', '')
#             razorpay_order_id = request.data.get('razorpay_order_id', '')
#             signature = request.data.get('razorpay_signature', '')
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }
#             print(params_dict)
#             #verify the payment signature.
#             result = razorpay_client.utility.verify_payment_signature(params_dict)
#             print(result)
#             if result is None:
#                 try:
#                     # capture the payemt
#                     razorpay_client.payment.capture(payment_id, amount)
#                     # render success page on successful caputre of payment
#                     return Response({"status":"success","message":"Payment Success!"},status=status.HTTP_201_CREATED)
#                 except:
#                     # if there is an error while capturing payment.
#                     return Response({"status": "warning", "message": "Payment Failed!"},status=status.HTTP_406_NOT_ACCEPTABLE)

#             else:
#                 # if signature verification fails.
#                 return Response({"status": "warning", "message": "Invalid Payment!"},status=status.HTTP_406_NOT_ACCEPTABLE)
#         except:
#             # if we don't find the required parameters in POST data
#             return Response({"status": "warning", "message": "Invalid Inputes!"},status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render
import razorpay
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
# from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import render,get_object_or_404


# client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))
# client.order.payment(orderId)

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

# Razorpay Payment Create
class RazorPayCreatePaymentAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.data)

        # userObj = self.request.user.id

        currency = 'INR'
        amount = 300 * 100  # Rs. 200
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                           currency=currency,
                                                           payment_capture="0"))
        print(razorpay_order)

        return Response({"razorpay_order": razorpay_order}, status=status.HTTP_200_OK)

class RazorPayVerifyPaymentAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        #print(request.data)

        # userObj = self.request.user

        currency = 'INR'
        amount = 200 * 100  # Rs. 200

        try:
            # get the required parameters from post request.
            payment_id = request.data.get('razorpay_payment_id', '')
            razorpay_order_id = request.data.get('razorpay_order_id', '')
            signature = request.data.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            print(params_dict)
            #verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            print(result)
            if result is None:
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
                    # render success page on successful caputre of payment
                    return Response({"status":"success","message":"Payment Success!"},status=status.HTTP_201_CREATED)
                except:
                    # if there is an error while capturing payment.
                    return Response({"status": "warning", "message": "Payment Failed!"},status=status.HTTP_406_NOT_ACCEPTABLE)

            else:
                # if signature verification fails.
                return Response({"status": "warning", "message": "Invalid Payment!"},status=status.HTTP_406_NOT_ACCEPTABLE)
        except:
            # if we don't find the required parameters in POST data
            return Response({"status": "warning", "message": "Invalid Inputes!"},status=status.HTTP_400_BAD_REQUEST)


