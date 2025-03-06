from django.contrib.auth.models import User
from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    current_price = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=10000)  # Starting virtual money

    def __str__(self):
        return f"{self.user.username}'s Portfolio"

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_transaction = models.FloatField()
    transaction_type = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.quantity} {self.stock.symbol}"
