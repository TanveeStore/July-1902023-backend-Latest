from channels.consumer import SyncConsumer, AsyncConsumer
from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from common.models import User
# from .models import Thread




class ChatConsumer(WebsocketConsumer):

    def connect(self):

        # create a room for chat. in this 
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.group_name = f'room_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

        # async_to_sync(self.channel_layer.group_send)(
        #     f'room_{self.room_name}', {
        #         'value' : json.dumps({'status': 'online'})
        #     }
        # )

        data = {'type' : 'connected'}


        self.send(text_data = json.dumps({
            'payload' : 'connected'
        }))


    def receive(self, text_data):
        data = json.loads(text_data)

        payload = {'message' : data.get('message'), 'sender': data.get('sender')}

        # print(data) 

        async_to_sync(self.channel_layer.group_send)(
            f'room_{self.room_name}', {
                'type' : 'send_message',
                'value' : json.dumps(payload)
            }
        )


    def disconnect(self, close_code):
        print((f'[{self.channel_name}] - Disconnected'))
        async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)


    def send_message(self, text_data):
        # print(type(text_data))
        # data = text_data.get('value')

        data = json.loads(text_data.get('value'))

        self.send(text_data = json.dumps({
            'payload' : data
        }))



class NewChatConsumer(WebsocketConsumer):

    def connect(self):

        me = self.scope['user']
        other_name = self.scope['url_route']['kwargs']['first_name']
        print(other_name)

        # otherUserObject = User.objects.get(first_name = other_name)
        # create a room for chat. in this 
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.group_name = f'room_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

        # async_to_sync(self.channel_layer.group_send)(
        #     f'room_{self.room_name}', {
        #         'value' : json.dumps({'status': 'online'})
        #     }
        # )

        data = {'type' : 'connected'}


        self.send(text_data = json.dumps({
            'payload' : 'connected'
        }))


    def receive(self, text_data):
        data = json.loads(text_data)

        payload = {'message' : data.get('message'), 'sender': data.get('sender')}

        # print(data) 

        async_to_sync(self.channel_layer.group_send)(
            f'room_{self.room_name}', {
                'type' : 'send_message',
                'value' : json.dumps(payload)
            }
        )


    def disconnect(self, close_code):
        print((f'[{self.channel_name}] - Disconnected'))
        async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)


    def send_message(self, text_data):
        # print(type(text_data))
        # data = text_data.get('value')

        data = json.loads(text_data.get('value'))

        self.send(text_data = json.dumps({
            'payload' : data
        }))



# class PersonalConsumer(SyncConsumer):
#     def websocket_connect(self, event):
        
#         meObj = self.scope['user'].id
#         print(meObj)
#         # if meObj.is_authenticated:
#         #     print(meObj)
#         # else:
#         #     print("user not found", meObj)
#         otherUsernameObj = self.scope['url_route']['kwargs']['first_name']
#         OtheruserObj = User.objects.get(first_name= otherUsernameObj)
#         print(OtheruserObj)
#         threadObj = Thread.objects.get_or_create_personal_thread(meObj, OtheruserObj)
#         self.room_name = f'personal_thread_{threadObj.id}'
        
#         async_to_sync(self.channel_layer.group_add)(self.room_name, self.channel_name)
        
#         self.send({
#             'type':'websocket.accept'
#         })
#         print(f'[{self.channel_name} - you are connected]')

#     def websocket_receive(self, event):
#         print(f'[{self.channel_name}] - Received message- {event["text"]}')
        
#         msg = json.dumps({
#             'text': event.get('text'),
#             'first_name': self.scope['user'].first_name
#         })
#         async_to_sync(self.channel_layer.group_send)(self.room_name,
#         {
#             'type': 'websocket.message',
#             'text': msg
#             # 'text': event.get('text')
#         }
#         )

#     def websocket_message(self, event):
#         print(f'[{self.channel_name}] - Message sent - {event["text"]}')
#         self.send({
#             'type': "websocket_send",
#             'text' : event.get('text'),
#         })
    
#     def websocket_disconnect(self, event):
#         print((f'[{self.channel_name}] - Disconnected'))
#         async_to_sync(self.channel_layer.group_discard)(self.room_name, self.channel_name)

