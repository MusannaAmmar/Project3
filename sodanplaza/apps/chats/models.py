from django.db import models
from apps.users.models import CustomUser



def generate_room_name(sender,receiver):
    return f'room_{min(sender.id,receiver.id)}_{max(sender.id,receiver.id)}'


class ChatMessage(models.Model):
    sender= models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='send_messages')
    receiver= models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='message_receiver')
    message=models.TextField(null=True,blank=True)
    timestamp= models.DateTimeField(auto_now_add=True)
    room_name= models.CharField(max_length=300,null=True,blank=True)
    is_seen= models.BooleanField(default=False)
    seen_at= models.DateTimeField(null=True,blank=True)
    is_archived= models.BooleanField(default=False)
    media= models.ImageField(upload_to='chat/media',null=True,blank=True)

    def __str__(self):
        return f'Message from {self.sender} to {self.receiver} at{self.timestamp}'

class Notification(models.Model):
    user= models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    message= models.ForeignKey(ChatMessage,on_delete=models.CASCADE,null=True,blank=True)
    is_read= models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name

class Community(models.Model):
    name= models.CharField(max_length=150,null=True,blank=True)
    description= models.CharField(max_length=200,null=True,blank=True)
    display_picture= models.ImageField(upload_to='community/chat/dp/',null=True,blank=True)
    admin= models.ManyToManyField('users.CustomUser',null=True,blank=True)
    members=models.ManyToManyField('users.CustomUser',null=True,blank=True)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name    


class CommunityMessage(models.Model):
    community= models.ForeignKey(Community,on_delete=models.CASCADE,related_name='community_notes')
    sender= models.ForeignKey('users.CustomUser',on_delete=models.CASCADE,null=True,blank=True)
    message= models.TextField()
    timestamp= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.email} to {self.community.name}'
    
class MediaUpload(models.Model):
    title= models.CharField(max_length=200,null=True,blank=True)
    media= models.FileField(upload_to='chat/media',null=True,blank=True)
    upload_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
