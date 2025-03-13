from rest_framework import serializers
from apps.chats.models import*


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ChatMessage
        fields='__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Notification
        fields='__all__'

class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Community
        fields='__all__'

class CommunityMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model= CommunityMessage
        fields='__all__'


class MediaUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model=MediaUpload
        fields='__all__'

