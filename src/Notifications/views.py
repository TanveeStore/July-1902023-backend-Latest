from sre_constants import SUCCESS
from django.shortcuts import render
from Notifications.models import Notifications
from Notifications.serializers import NotificationsSerializer
from rest_framework.response import Response
from common.models import User
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.views import APIView

# Notifiactions API View
class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        notificationObj = Notifications.objects.filter(user=userObj)
        NotificationData = NotificationsSerializer(notificationObj, many=True).data


        return Response(
            {
                "status": "success",
                "messsage": "Notification Feched Successfully",
                "data": NotificationData

            }, status=200
        )

    def post(self, request):
        userObj = User.objects.get(id=self.request.user.id)
        notificationId = request.data.get("id", None)
        
        
        
        if notificationId == None:
            return Response(
                {
                    "status": "warning",
                    "message": "You Don't have Notifications"
                    
                }, status=200
            )
        else:
            try:
                notificationObj = Notifications.objects.get(user=userObj, id=notificationId)
                notificationObj.seenStatus = True
                notificationObj.save()
                return Response(
                    {
                        "status": "success",
                        "Message": "Notification Seen Successfully"
                    }, status=200
                )
            except Notifications.DoesNotExist:
                return Response(
                    {
                        "status": "warning",
                        "Message": "Invalid Notification Id"
                    }, status=200
                )


