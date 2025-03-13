from rest_framework import serializers
from apps.administration.models import*

class VideoTutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model=VideoTutorial
        fields= '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields= '__all__'

class SubcategorySerialzer(serializers.ModelSerializer):
    class Meta:
        model= SubCategory
        fields= '__all__'

class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model= SiteSettings
        fields= '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model= Language
        fields='__all__'