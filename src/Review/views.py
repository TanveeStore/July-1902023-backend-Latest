from django.shortcuts import render
from Review.models import ProductReview
from products.models import Product
from Review.serializers import ProdcutReviewSerializer, ReviewSerializer
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.db.models import Max,Min,Count,Avg
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import DestroyAPIView



# Create your views here.
class ProductReviewApi(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        review = ProductReview.objects.filter(user=user).order_by('-id')
        user_product_review_serializer_data = ProdcutReviewSerializer(review, many=True).data

        if len(user_product_review_serializer_data)>0:
            responseData = {
                "status": "success",
                "message": "Review list found",
                "data": user_product_review_serializer_data
            }
            return Response(responseData, status=status.HTTP_200_OK)
        else:
            responseData = {
                "status": "warning",
                "message": "You don't have any posted review!"
            }
            return Response(responseData, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):

        user = self.request.user
        product = Product.objects.get(
            id=request.data['product'])
        comment = request.data.get('comment', False)
        rating = request.data.get('rating', False)


        review = ProductReview.objects.create(
            user=user,
            product=product,
            comment=comment,
            rating=rating
        )

        # Fetch avg rating for reviews
        avg_reviews = ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))
        #print(str(review))
        print(avg_reviews)
        # End
        data ={
            "user":(user.first_name +" " + user.last_name),
            "product":product.name,
            "comment":comment,
            "rating":rating,
            "avg_ratings":avg_reviews
        }
        return Response(
            {"error": False, "data":data, "message": "Review Successfully Posted"},
            status=status.HTTP_200_OK
        )



class DestroyProductReviewAPIView(DestroyAPIView):

    permission_classes = [IsAuthenticated,]
    serializer_class = ProdcutReviewSerializer
    queryset = ProductReview.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        responseData = {
            "status": "success",
            "message": "This Review is Successfully deleted!!"
        }
        return Response({"detail": responseData}, status=status.HTTP_200_OK)