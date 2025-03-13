from apps.profession.models import*
from rest_framework import serializers


class GigSerializer(serializers.ModelSerializer):
    class Meta:
        model= Gig
        fields= '__all__'

class GigSelectedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model= GigSelectedService
        fields= '__all__'

class GigReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model= GigReview
        fields= '__all__'

class GigFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model= GigFaq
        fields= '__all__'

class RequestAttachAgencySerializer(serializers.ModelSerializer):
    class Meta:
        model=RequestAttachAgency
        fields= '__all__'

class GigLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model= GigLanguage
        fields= '__all__'

class GigGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model= GigGallery
        fields= '__all__'


class GigSelectedLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model= GigSelectedLocation
        fields= '__all__'