from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    volatility = models.DecimalField(max_digits=5, decimal_places=2, help_text="Max percentage change per tick")

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class Portfolio(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='portfolios')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    average_buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.user.username} - {self.stock.symbol} : {self.quantity}"

class Scenario(models.Model):
    SCENARIO_TYPES = [
        ('SCAM', 'UPI Scam'),
        ('TAX', 'Tax Challenge'),
    ]
    type = models.CharField(max_length=10, choices=SCENARIO_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    correct_action = models.CharField(max_length=50, help_text="e.g., 'DECLINE', 'REPORT', 'PAY'")
    xp_reward = models.IntegerField(default=50)
    penalty = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)

    def __str__(self):
        return f"[{self.type}] {self.title}"
