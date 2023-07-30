from rest_framework import serializers
from Notifications.models import Notifications


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields ="__all__"

# Notifiaction Status Seen Seriializer
# class NotificationSeenSerializer(serializers.Serializer):
    
#     notificationId = serializers.IntegerField(blank = False, null = False)
#     seenStatus = serializers.BooleanField(default = True)
