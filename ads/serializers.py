from rest_framework import serializers
from .models import Ad, ExchangeProposal

class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ad
        fields = ['id', 'title', 'description', 'image_url', 'category', 'condition']  # Явное указание полей

class ExchangeProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeProposal
        fields = '__all__'
