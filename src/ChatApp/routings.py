from django.urls import path
from ChatApp import consumers


# set the route for consumers
websocket_urlpatterns = [
    path('chat/<room_code>', consumers.ChatConsumer.as_asgi()),
    path('ws/chat/<str:first_name>', consumers.NewChatConsumer.as_asgi()), 
    # path('ws/chat1/<str:first_name>', consumers.PersonalConsumer.as_asgi()),
]