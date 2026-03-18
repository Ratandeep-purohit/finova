from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Stock, Portfolio, Scenario

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'balance', 'xp', 'level']

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    name = serializers.CharField(source='stock.name', read_only=True)
    current_price = serializers.DecimalField(source='stock.current_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'symbol', 'name', 'quantity', 'average_buy_price', 'current_price']

class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scenario
        fields = ['id', 'type', 'title', 'description', 'xp_reward', 'penalty'] # hide correct_action
