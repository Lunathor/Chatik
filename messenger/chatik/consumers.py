from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Подключаем пользователя к группе WebSocket
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        user = self.scope['user']

        if not user.is_authenticated:
            return  # Не отправляем сообщение от неаутентифицированных пользователей

        # Отправка сообщения группе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'chat_id': self.room_name,  # Добавляем ID чата
                'user': {
                    'username': user.username,
                    'avatar': user.avatar.url if user.avatar else '/media/avatars/default-avatar.jpeg',
                }
            }
        )

    async def chat_message(self, event):
        message = event['message']
        chat_id = event['chat_id']  # Получаем ID чата

        # Отправляем сообщение на клиент
        await self.send(text_data=json.dumps({
            'message': message,
            'chat_id': chat_id,  # Отправляем ID чата на клиент
            'user': event['user']
        }))