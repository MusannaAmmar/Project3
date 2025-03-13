from rest_framework import serializers
from apps.agency.models import *

class AgencyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= AgencyProfile
        fields='__all__'

class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= OwnerProfile
        fields= '__all__'


class AgencyGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model= AgencyGallery
        fields= '__all__'

class AgencyServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model= AgencyServices
        fields= '__all__'

class AgencyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model= AgencyReview
        fields='__all__'

class AgencyEmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model= AgencyEmploye
        fields= '__all__'