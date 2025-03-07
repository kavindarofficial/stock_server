from django.urls import path
from .views import register, login, buy_stock, sell_stock

urlpatterns = [
    path("register/", register),
    path("login/", login),
    path("buy/", buy_stock),
    path("sell/", sell_stock),
]
