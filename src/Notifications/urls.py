from django.urls import path
from Notifications import views


app_name = 'Notifications'

urlpatterns = [
    path("notification/", views.NotificationAPIView.as_view()),

]
    