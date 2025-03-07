from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=1500.0)  # Initial balance of $1500
    stocks = models.JSONField(default=dict)  # Stores owned stocks in {'AAPL': 2, 'GOOGL': 3} format

    def __str__(self):
        return self.user.username
