from .models import Subscription, SubscribedTransaction
from rest_framework import serializers

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('__all__')

class SubscribedTransactionSerializer(serializers.ModelSerializer):
    pricing_info = serializers.SerializerMethodField()
    token_info = serializers.SerializerMethodField()

    def get_pricing_info(self, obj):
        if not obj.price_lookup:
            return {}
        return obj.get_pricing_info()
    
    def get_token_info(self, obj):
        token = obj.get_token()
        
        if not token:
            return {}
        
        return {
            'symbol': token.symbol,
            'nickname': token.nickname,
            'decimal_places': token.decimal_places,
            'contract': token.contract.address
        }

    class Meta:
        model = SubscribedTransaction
        fields = ('__all__')

