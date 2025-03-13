from rest_framework import serializers
from apps.users.models import*

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= UserProfile
        fields= '__all__'


class ProfessionProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= ProfessionProfile
        fields= '__all__'
        extra_kwargs= {
            'ratings_count':{'write_only':True}
        }
class ProfessionSelectedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model= ProfessionSelectedService
        fields='__all__'