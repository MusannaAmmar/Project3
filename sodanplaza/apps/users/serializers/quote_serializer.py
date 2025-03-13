from rest_framework import serializers
from apps.users.models import*

class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model= Quote
        fields='__all__'

        