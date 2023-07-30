from django.contrib import admin
from Notifications.models import Notifications

# Register your models here.
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "notificationText", "notificationType", "seenStatus", "created_at"]
    list_per_page = 25
admin.site.register(Notifications, NotificationsAdmin)