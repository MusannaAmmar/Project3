import json
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.chats.models import generate_room_name
from channels.db import database_sync_to_async
from apps.users.models import*
from apps.chats.models import*
from django.utils.timezone import now
from channels.db import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name= self.scope['url_route']['kwargs']['room_name']
        self.room_group_name= f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
        await self.accept()
        user_ids= (int(id) for id in self.room_name.split('_')[1:]) 
        logged_in_user_id=self.scope['user'].id

        # Determine the receiver (the other user in the chat)
        receiver_id= next((id for id in user_ids if id !=logged_in_user_id),None)
        receiver= await self.get_user_by_username(receiver_id)

        #Mark all unseen messages in this room as seen

        await self.mark_message_seen(self.room_name,receiver)

    async def disconnect(self,close_data):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self,text_data):
        data=json.loads(text_data)
        sender_username= data['sender']
        receiver_username= data['receiver']
        message=data['message']
        media=data['media']
        
        #Use Database_sync_to_async to handle ORM queries

        receiver= await self.get_user_by_username(sender_username)
        sender= await self.get_user_by_username(receiver_username)
        room_name=generate_room_name(receiver,sender)

        #Save the message and notification in database
        chat_message= await self.save_message(sender,receiver,room_name,media=media)
        await self.create_notification(receiver,chat_message)

        # Mark messages as seen for this room and User

        await self.mark_message_seen(room_name,receiver)

        # Send the Message to the WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'receiver':receiver,
                'sender':sender,
                'timestamp':chat_message.timestamp,
                'media':chat_message.media
            }
        )

    @database_sync_to_async
    def get_user_by_username(self,username):
        return CustomUser.objects.get(id=username)
    
    @database_sync_to_async
    def mark_message_seen(self,room_name,user):
        ChatMessage.objects.filter(room_name=room_name,receiver=user,is_seen=False).update(is_seen=True,seen_at=now())

    @database_sync_to_async
    def save_message(self,sender,receiver,room_name,media):
        ChatMessage.objects.create(sender=sender,receiver=receiver,room_name=room_name,media=media)
    
    @database_sync_to_async
    def create_notification(self,receiver,chat_message):
        Notification.objects.create(user=receiver,message=chat_message)

    @database_sync_to_async
    def mark_message_seen(self,room_name,user):
        ChatMessage.objects.filter(room_name=room_name,receiver=user,is_seen=False).update(is_seen=True,seen_at=now())

    @database_sync_to_async
    def get_unread_stats(self,user):
        unread_messages= ChatMessage.objects.filter(receiver=user,is_seen=False).count()
        unread_notification= Notification.objects.filter(user= user,is_seen=False).count()
        return {'Unread Messages':unread_messages,'Unread Notification':unread_notification}
    
    async def chat_message(self,event):
        message=event['message']
        sender= event['sender']
        receiver=event['receiver']
        timestamp=event['timestamp']
        media=event['media']

        await self.send(text_data=json.dumps({
            'message':message,
            'sender':sender.id,
            'receiver':receiver.id,
            'timestamp':str(timestamp),
            'media':str(media)
        }))

    async def seen_messages(self,room_name,user):
        await self.mark_message_seen(room_name,user)
    
    async def user_stats(self,user):
        stats=  await self.get_unread_stats(user)
        await self.send(text_data=json.dumps(stats))



class CommunityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.community_id= self.scope['url_route']['kwargs']['community_id']
        self.community_group_name= f'community_{self.community_id}'

        #Check if the community exists and the user is a member
        user= self.scope['user']
        self.community= await sync_to_async(Community.objects.get)(id=self.community_id)

        if not user.is_authenticated or not await sync_to_async(self.community.members.filter)(id=user.id).exist():
            await self.close()
            return
        
        # Add user to the Webscocket group

        await self.channel_layer.add_group(
            self.community_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self,close_code):
        await self.channel_layer.discard_group(
            self.community_group_name,
            self.channel_name,
        )

    async def receive(self,text_data):
        data=json.loads(text_data)
        user= self.scope['user']

        # check if the user is authencticated
        if not user.is_authenticated:
            await self.send(json.dumps({'error':'Authentication Required'}))
            return
        
        if not await sync_to_async(self.community.admin.filter)(id=user.id).exist():
            await self.send(json.dumps({'error':'Only Admins can send messages'}))
            return
        
        message= data.get('message')
        chat_message=await sync_to_async(ChatMessage.objects.create(
            community=self.community,
            sender= user,
            message= message,
        ))

        #Broadcast the message to the group

        await self.channel_layer.group_send({
            'type':'community_message',
            'mesage':message,
            'message':user.username,
            'timestamp':str(chat_message.timestamp),
        })

    async def community_message(self,event):
        await self.send(json.dumps({
            'message':event['message'],
            'sender':event['sender'],
            'timestamp':event['timestamp']
            
        }))















