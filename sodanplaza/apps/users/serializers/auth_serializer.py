from rest_framework import serializers
from apps.users.models import *

class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomUser
        fields= '__all__'
        extra_kwargs= {
            'password':{'write_only':True},
            'otp':{'write_only':True}
        }

    def create(self,validated_data):
        user= CustomUser.objects.create_user(**validated_data)
        user.generate_otp()
        return user
    
class OtpVerificatgionSerializer(serializers.Serializer):
    email= serializers.CharField(max_length=100)
    otp= serializers.CharField(max_length=6)

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomUser
        fields= ['email','password']

class ForgotPasswordSerializer(serializers.Serializer):
    email= serializers.EmailField()

    def validate_email(self,value):
        try:
            user= CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise ValueError('User with this email does not exist')
        return value
        
    def save(self):
        email= self.validated_data['email']
        user= CustomUser.objects.get(email=email)
        user.generate_otp()
        return user
    